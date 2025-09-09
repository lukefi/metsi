# Licensed under the Mozilla Public License 2.0 (MPL-2.0).
#
# NOTE:
# This file imports code from MetsiGrow.
# MetsiGrow is NOT licensed under MPL-2.0.
# MetsiGrow is released under a separate Source Available – Non-Commercial license.
# See MetsiGrow's LICENSE-NC.md for full details.
from typing import Optional,TypeVar
from functools import cached_property
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

    def __init__(self, stand: ForestStand, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)  # type: ignore[misc]
        except TypeError:
            pass
        self.stand = stand  # store stand for property access

    # -- site variables --------------------

    @property
    def year(self) -> int:
        return _require(self.stand.year, "stand.year")

    @property
    def get_y(self) -> float:
        if self.stand.geo_location is None or self.stand.geo_location[0] is None:
            return 0.0
        return self.stand.geo_location[0]

    @property
    def get_x(self) -> float:
        if self.stand.geo_location is None or self.stand.geo_location[1] is None:
            return 0.0
        return self.stand.geo_location[1]


    @property
    def dd(self) -> float:
        assert self.stand.degree_days is not None, "stand.geo_location must be set"
        return self.stand.degree_days

    @property
    def sea(self) -> float:
        return _require(self.stand.sea_effect, "stand.sea_effect")

    @property
    def lake(self) -> float:
        return _require(self.stand.lake_effect, "stand.lake_effect")

    @property
    def mal(self) -> LandUseCategoryVMI:
        return LandUseCategoryVMI(self.stand.land_use_category)

    @property
    def mty(self) -> SiteTypeVMI:
        return SiteTypeVMI(self.stand.site_type_category)

    @property
    def alr(self) -> SoilCategoryVMI:
        return SoilCategoryVMI(self.stand.soil_peatland_category)

    @property
    def verl(self) -> TaxClass:
        return TaxClass(self.stand.tax_class)

    @property
    def verlt(self) -> TaxClassReduction:
        return TaxClassReduction(self.stand.tax_class_reduction)

    # -- management vars (defaults) --------



    @property
    def spedom(self) -> Species:
        """
        Dominant species (MetsiGrow Species):
        1) Choose by total basal area per species.
        2) If all basal areas are zero/unavailable, fall back to stems/ha.

        If to_mg_species fails for any tree, this property raises ValueError (no swallowing).
        """
        # 1) Basal area aggregation by Species
        ba_by_species: dict[Species, float] = defaultdict(float)
        for t in getattr(self.stand, "reference_trees", []):
            # If t.species is None, you may keep your default (PINE) or change as needed
            sp = to_mg_species(t.species if t.species is not None else Species.PINE)
            ba_by_species[sp] += float(calculate_basal_area(t) or 0.0)

        if any(v > 0.0 for v in ba_by_species.values()):
            return max(ba_by_species.items(), key=lambda kv: kv[1])[0]

        # 2) Fallback: stems/ha
        stems_by_species: dict[Species, float] = defaultdict(float)
        for t in getattr(self.stand, "reference_trees", []):
            sp = to_mg_species(t.species if t.species is not None else Species.PINE)
            stems_by_species[sp] += float(getattr(t, "stems_per_ha", 0.0) or 0.0)

        if stems_by_species:
            return max(stems_by_species.items(), key=lambda kv: kv[1])[0]

        # Sensible fallback if no trees present
        return Species.DECIDUOUS

    @property
    def prt(self) -> Origin:
        return Origin.NATURAL

    # -- tree variables --------------------

    @cached_property
    def trees_f(self) -> list[float]:
        if self.stand.reference_trees is None:
            return [0.0]
        return [(t.stems_per_ha or 0.0) for t in self.stand.reference_trees]

    @cached_property
    def trees_d(self) -> list[float]:
        return [(t.breast_height_diameter or 0.01) for t in self.stand.reference_trees]

    @cached_property
    def trees_h(self) -> list[float]:
        return [(t.height or 0.0) for t in self.stand.reference_trees]

    @cached_property
    def trees_spe(self) -> list[Species]:
        converted = []
        for t in self.stand.reference_trees:
            try:
                converted.append(to_mg_species(t.species or Species.PINE))
            except Exception as e:
                print(f"[SpeciesError] Invalid tree species: {t.species} → {e}")
                raise
        return converted

    @cached_property
    def trees_t0(self) -> list[float]:
        return [int((self.year or 0) - (t.biological_age or 0.0)) for t in self.stand.reference_trees]

    @cached_property
    def trees_t13(self) -> list[float]:
        return [self.year - (t.breast_height_age or 0.0) for t in self.stand.reference_trees]

    @cached_property
    def trees_storie(self) -> list[Storie]:
        # TODO: derive or import storie data
        return [Storie.NONE for _ in self.stand.reference_trees]

    @cached_property
    def trees_snt(self) -> list[Origin]:
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
    diameters = [t.breast_height_diameter + d for t, d in zip(stand.reference_trees, growth.trees_id)]
    heights   = [t.height + h for t, h in zip(stand.reference_trees, growth.trees_ih)]
    stems     = [(t.stems_per_ha or 0.0) + df for t, df in zip(stand.reference_trees, growth.trees_if)]

    update_stand_growth(stand, diameters, heights, stems, step)

    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if (t.stems_per_ha or 0.0) >= 1.0]
    return stand, None