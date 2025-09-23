# Licensed under the Mozilla Public License 2.0 (MPL-2.0).
#
# NOTE:
# This file imports code from MetsiGrow.
# MetsiGrow is NOT licensed under MPL-2.0.
# MetsiGrow is released under a separate Source Available – Non-Commercial license.
# See MetsiGrow's LICENSE-NC.md for full details.


from typing import Sequence
import numpy as np

from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.enums.internal import (
    TreeSpecies,
    CONIFEROUS_SPECIES,
    DECIDUOUS_SPECIES,
)
from lukefi.metsi.data.vector_model import ReferenceTrees
from lukefi.metsi.domain.natural_processes.util import update_stand_growth_vectorized
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.data.layered_model import PossiblyLayered

# Lower-level MetsiGrow types
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


# ---------- helpers ----------

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


def _require(val, name: str):
    if val is None:
        raise ValueError(f"{name} must be set before prediction")
    return val


def _origin_to_mg(o: int) -> Origin:
    # In AoS version: Origin(t.origin + 1) if set, else NATURAL
    try:
        return Origin(int(o) + 1) if o is not None and int(o) >= 0 else Origin.NATURAL
    except ValueError:
        return Origin.NATURAL


def _nan_to_num(a: np.ndarray, nan: float = 0.0) -> np.ndarray:
    return np.nan_to_num(a, nan=nan, posinf=nan, neginf=nan)


# ---------- vectorized predictor ----------

class MetsiGrowPredictorVec(Predict):
    """
    Extend metsi_grow.Predict to interface ForestStand & ReferenceTree data.
    """

    def __init__(self, stand: PossiblyLayered[ForestStand]) -> None:
        super().__init__()
        self.stand = stand
        self.year = float(_require(stand.year, "stand.year"))

        # stand/site properties
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

        # tax class reduction optional
        verlt_raw = stand.tax_class_reduction
        self.verlt = TaxClassReduction(
            int(getattr(verlt_raw, "value", verlt_raw)) if verlt_raw is not None
            else int(TaxClassReduction.NONE)
        )

        self.dd = stand.degree_days or 0.0
        self.sea = stand.sea_effect or 0.0
        self.lake = stand.lake_effect or 0.0

        tc_raw = stand.tax_class
        val = int(getattr(tc_raw, "value", tc_raw) or 0)
        if val:
            self.verl = TaxClass(val)

        # management variables
        self.prt = Origin.NATURAL

        # tree variables from SoA
        rt = self._require_rtrees()

        # stems/ha
        self.trees_f = self._trees_f(rt)
        # diameters (ensure minimal positive value like AoS 0.01)
        self.trees_d = self._trees_d(rt)
        # heights
        self.trees_h = self._trees_h(rt)
        # years since t0 and t13
        self.trees_t0 = self._trees_t0(rt)   # year - biological_age
        self.trees_t13 = self._trees_t13(rt) # year - breast_height_age
        # storie placeholder
        self.trees_storie = [Storie.NONE] * rt.size
        # origin per tree
        self.trees_snt = self._trees_snt(rt)
        # species per tree (MetsiGrow)
        self._trees_spe_cache: list[Species] | None = None
        self._spedom_cache: Species | None = None

    # --- required tree vectors ---

    def _require_rtrees(self) -> ReferenceTrees:
        rt = self.stand.reference_trees_soa
        if rt is None:
            raise MetsiException("Reference trees not vectorized")
        return rt

    def _trees_f(self, rt: ReferenceTrees) -> list[float]:
        return _nan_to_num(rt.stems_per_ha, 0.0).tolist()

    def _trees_d(self, rt: ReferenceTrees) -> list[float]:
        d = _nan_to_num(rt.breast_height_diameter, 0.01)
        d = np.where(d <= 0.0, 0.01, d)
        return d.tolist()

    def _trees_h(self, rt: ReferenceTrees) -> list[float]:
        return _nan_to_num(rt.height, 0.0).tolist()

    def _trees_t0(self, rt: ReferenceTrees) -> list[int]:
        # int((year or 0) - (bio_age or 0.0))
        bio = _nan_to_num(rt.biological_age, 0.0)
        return (self.year - bio).astype(int).tolist()

    def _trees_t13(self, rt: ReferenceTrees) -> list[int]:
        bha = _nan_to_num(rt.breast_height_age, 0.0)
        return (self.year - bha).astype(int).tolist()

    def _trees_snt(self, rt: ReferenceTrees) -> list[Origin]:
        # Origin(v+1) if v set (>=0), else NATURAL
        out: list[Origin] = []
        for v in rt.origin.tolist():
            out.append(_origin_to_mg(v))
        return out

    # --- dominant species and per-tree species ---

    @property
    def trees_spe(self) -> Sequence[Species]:
        if self._trees_spe_cache is None:
            rt = self._require_rtrees()
            conv: list[Species] = []
            for v in rt.species.tolist():
                conv.append(to_mg_species(v))

            self._trees_spe_cache = conv
        return self._trees_spe_cache

    @trees_spe.setter
    def trees_spe(self, value) -> None:
        self._trees_spe_cache = list(value)

    @property
    def spedom(self) -> Species:
        if self._spedom_cache is None:
            self._spedom_cache = self._compute_spedom_from_stand_soa()
        return self._spedom_cache

    @spedom.setter
    def spedom(self, value: Species) -> None:
        self._spedom_cache = value

    def _compute_spedom_from_stand_soa(self) -> Species:
        rt = self._require_rtrees()
        if rt.size == 0:
            raise ValueError("Cannot determine dominant species: no reference trees.")

        # convert species for each tree
        mg_species = [to_mg_species(v for v in rt.species.tolist())]

        # basal area per tree: stems_per_ha * pi * (0.005 * d)^2  (d in cm → m radius)
        d = _nan_to_num(rt.breast_height_diameter, 0.0)
        f = _nan_to_num(rt.stems_per_ha, 0.0)
        ba_per_tree = f * np.pi * (0.01 * 0.5 * d) ** 2

        # aggregate by species
        ba_by_species: dict[Species, float] = {}
        for s, ba in zip(mg_species, ba_per_tree.tolist()):
            ba_by_species[s] = ba_by_species.get(s, 0.0) + float(ba)

        if any(v > 0.0 for v in ba_by_species.values()):
            return max(ba_by_species.items(), key=lambda kv: kv[1])[0]

        # fallback to stems
        stems_by_species: dict[Species, float] = {}
        for s, stems in zip(mg_species, f.tolist()):
            stems_by_species[s] = stems_by_species.get(s, 0.0) + float(stems)

        if any(v > 0.0 for v in stems_by_species.values()):
            return max(stems_by_species.items(), key=lambda kv: kv[1])[0]

        raise ValueError("Cannot determine dominant species: all basal areas and stem counts are zero.")


# ---------- public API  ----------

def grow_metsi_vec(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    """
    Wrapper for metsi_grow. Applies growth step to ForestStand.
    Assumes input is vectorized
    """
    step = operation_parameters.get("step", 5)
    stand, collected_data = input_
    if stand.reference_trees_soa is None:
        raise MetsiException("Reference trees not vectorized")
    if stand.reference_trees_soa.size == 0:
        return input_

    # build predictor and run growth
    pred = MetsiGrowPredictorVec(stand)
    growth = pred.evolve(step=step)

    rt = stand.reference_trees_soa

    # deltas from MetsiGrow
    idelta = np.asarray(growth.trees_id, dtype=float)  # diameter increments
    hdelta = np.asarray(growth.trees_ih, dtype=float)  # height increments
    fdelta = np.asarray(growth.trees_if, dtype=float)  # stems/ha increments

    # apply deltas to get absolute new values
    diameters = _nan_to_num(rt.breast_height_diameter, 0.0) + idelta
    heights   = _nan_to_num(rt.height, 0.0) + hdelta
    stems     = _nan_to_num(rt.stems_per_ha, 0.0) + fdelta

    # update stand in-place
    update_stand_growth_vectorized(stand, diameters, heights, stems, step)

    # prune dead trees (stems < 1.0)
    to_delete = np.nonzero(stems < 1.0)[0]
    if to_delete.size > 0:
        stand.reference_trees_soa.delete(to_delete.tolist())

    return stand, collected_data
