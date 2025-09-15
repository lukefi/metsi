# Licensed under the Mozilla Public License 2.0 (MPL-2.0).
#
# NOTE:
# This file imports code from MetsiGrow.
# MetsiGrow is NOT licensed under MPL-2.0.
# MetsiGrow is released under a separate Source Available – Non-Commercial license.
# See MetsiGrow's LICENSE-NC.md for full details.

from typing import Optional,TypeVar, Sequence
from collections import defaultdict
from lukefi.metsi.forestry.forestry_utils import calculate_basal_area

from lukefi.metsi.data.enums.internal import (
    TreeSpecies,
    CONIFEROUS_SPECIES,
    DECIDUOUS_SPECIES,
)
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.natural_processes.util import update_stand_growth

# Lower-level MetsiGrow types (still used; no changes here)
from lukefi.metsi.forestry.naturalprocess.MetsiGrow.metsi_grow.chain import (
    Predict,
    Species,
    LandUseCategoryVMI,
    SiteTypeVMI,
    SoilCategoryVMI,
    TaxClass,
    TaxClassReduction,
    Origin,
    Storie,
)

def to_mg_species(code) -> Species:
    """
    Convert an internal species code to a MetsiGrow Species.

    Rules:
      - If `code` is already a Species, return it.
      - Else try to coerce to TreeSpecies; if that fails, raise ValueError.
      - If canonical (1..9), map directly to Species(code).
      - Else if belongs to CONIFEROUS_SPECIES or DECIDUOUS_SPECIES, return the bucket.
      - Otherwise raise ValueError.
    """
    if isinstance(code, Species):
        return code

    # Coerce to TreeSpecies or fail
    try:
        return Species(code)
    except ValueError as exc:
        try:
            ts = TreeSpecies(code)
        except ValueError as temp_exc:
            raise ValueError(f"Unknown tree species code: {code!r}") from temp_exc

        if ts in CONIFEROUS_SPECIES:
            return Species.CONIFEROUS
        if ts in DECIDUOUS_SPECIES:
            return Species.DECIDUOUS

        raise ValueError(f"Unsupported tree species code: {code!r}") from exc

T = TypeVar("T")

def _require(val: Optional[T], name: str) -> T:
    """
    Ensure a required value is set, else raise a ValueError.
    """
    if val is None:
        raise ValueError(f"{name} must be set before prediction")
    return val


class MetsiGrowPredictor(Predict):
    """
    Extend metsi_grow.Predict to interface ForestStand & ReferenceTree data.
    """

    def __init__(self, stand: ForestStand) -> None:
        super().__init__()
        self.stand = stand  # store stand for property access
        self.year = float(_require(stand.year, "stand.year"))
        y_coord = (stand.geo_location or (None, None))[0]
        x_coord = (stand.geo_location or (None, None))[1]
        self.get_y = float(y_coord or 0.0)
        self.get_x = float(x_coord or 0.0)
        mal_raw = _require(stand.land_use_category, "stand.land_use_category")
        self.mal = LandUseCategoryVMI(int(getattr(mal_raw, "value", mal_raw)))

        mty_raw = _require(stand.site_type_category, "stand.site_type_category")
        self.mty = SiteTypeVMI(int(getattr(mty_raw, "value", mty_raw)))

        alr_raw = _require(stand.soil_peatland_category, "stand.soil_peatland_category")
        self.alr = SoilCategoryVMI(int(getattr(alr_raw, "value", alr_raw)))

        # tax class reduction can be optional; default to NONE if missing
        verlt_raw = stand.tax_class_reduction
        self.verlt = TaxClassReduction(
            int(getattr(verlt_raw, "value", verlt_raw)) if verlt_raw is not None
            else int(TaxClassReduction.NONE)
        )
        self.dd  = self.stand.degree_days or 0.0
        self.sea  = self.stand.sea_effect or 0.0
        self.lake  = self.stand.lake_effect or 0.0

        tc_raw = stand.tax_class
        val = int(getattr(tc_raw, "value", tc_raw) or 0)
        if val:  # non-zero, valid
            self.verl = TaxClass(val)


        self.trees_f = self._trees_f()
        self.prt = Origin.NATURAL

        self.trees_d = self._trees_d()
        self.trees_h = self._trees_h()
        self.trees_t0 = self._trees_t0()
        self.trees_t13 = self._trees_t13()
        self.trees_storie = self._trees_storie()
        self.trees_snt = self._trees_snt()

        self._spedom_cache: Species | None = None
        self._trees_spe_cache: list[Species] | None = None

    @property
    def spedom(self) -> Species:
        if self._spedom_cache is None:
            self._spedom_cache = self._compute_spedom_from_stand()
        return self._spedom_cache

    @spedom.setter
    def spedom(self, value: Species) -> None:
        self._spedom_cache = value


    @property
    def trees_spe(self) -> Sequence[Species]:
        if self._trees_spe_cache is None:
            self._trees_spe_cache = self._trees_spe()
        return self._trees_spe_cache

    @trees_spe.setter
    def trees_spe(self, value) -> None:
        # Accept any Sequence[Species]; normalize to list
        self._trees_spe_cache = list(value)


    # -- management vars (defaults) --------

    def _compute_spedom_from_stand(self) -> Species:
        """
        Finds dominant species from MetsiGrow species.

        Rules:
          - Aggregate basal area per species; if any BA > 0, return the species with max BA.
          - Otherwise, aggregate stems_per_ha per species; if any stems > 0, return max stems.
          - If there are no reference trees, or both BA and stems are zero/missing, raise ValueError.
        """
        trees = getattr(self.stand, "reference_trees", None)
        if not trees:
            raise ValueError(
                "Cannot determine dominant species: stand has no reference trees."
            )

        # 1) Dominant by basal area
        ba_by_species: dict[Species, float] = defaultdict(float)
        for t in trees:
            sp = to_mg_species(t.species)
            ba_by_species[sp] += float(calculate_basal_area(t) or 0.0)

        if any(v > 0.0 for v in ba_by_species.values()):
            return max(ba_by_species.items(), key=lambda kv: kv[1])[0]

        # 2) Fallback to stems/ha
        stems_by_species: dict[Species, float] = defaultdict(float)
        for t in trees:
            sp = to_mg_species(t.species)
            stems_by_species[sp] += float(getattr(t, "stems_per_ha", 0.0) or 0.0)

        if any(v > 0.0 for v in stems_by_species.values()):
            return max(stems_by_species.items(), key=lambda kv: kv[1])[0]

        raise ValueError(
            "Cannot determine dominant species: all basal areas and stem counts are zero or missing."
        )



    # -- tree variables --------------------

    def _trees_f(self) -> list[float]:
        if self.stand.reference_trees is None:
            return [0.0]
        return [(t.stems_per_ha or 0.0) for t in self.stand.reference_trees]

    def _trees_d(self) -> list[float]:
        return [(t.breast_height_diameter or 0.01) for t in self.stand.reference_trees]

    def _trees_h(self) -> list[float]:
        return [(t.height or 0.0) for t in self.stand.reference_trees]

    def _trees_spe(self) -> list[Species]:
        converted = []
        for t in self.stand.reference_trees:
            try:
                converted.append(to_mg_species(t.species or Species.PINE))
            except Exception as e:
                print(f"[SpeciesError] Invalid tree species: {t.species} → {e}")
                raise
        return converted

    def _trees_t0(self) -> list[float]:
        return [int((self.year or 0) - (t.biological_age or 0.0)) for t in self.stand.reference_trees]

    def _trees_t13(self) -> list[float]:
        return [self.year - (t.breast_height_age or 0.0) for t in self.stand.reference_trees]

    def _trees_storie(self) -> list[Storie]:
        # TODO: derive or import storie data
        return [Storie.NONE for _ in self.stand.reference_trees]

    def _trees_snt(self) -> list[Origin]:
        return [
            Origin(t.origin + 1) if t.origin is not None else Origin.NATURAL
            for t in self.stand.reference_trees
        ]

# ---------- public API ----------

def grow_metsi(input_: tuple[ForestStand, None], /, **operation_parameters) -> tuple[ForestStand, None]:
    """
    Wrapper for metsi_grow evolve pipeline. Applies growth step to ForestStand.
    """
    step = operation_parameters.get("step", 5)
    stand, _ = input_

    # build predictor (use local class; no import from the old module path)
    pred = MetsiGrowPredictor(stand)
    growth = pred.evolve(step=step)

    # apply deltas
    diameters = [(t.breast_height_diameter or 0.0) + d for t, d in zip(stand.reference_trees, growth.trees_id)]
    heights   = [(t.height or 0.0) + h for t, h in zip(stand.reference_trees, growth.trees_ih)]
    stems     = [(t.stems_per_ha or 0.0) + df for t, df in zip(stand.reference_trees, growth.trees_if)]

    update_stand_growth(stand, diameters, heights, stems, step)

    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if (t.stems_per_ha or 0.0) >= 1.0]
    return stand, None
