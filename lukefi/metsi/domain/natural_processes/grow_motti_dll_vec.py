from typing import Optional, Dict, Union, Iterable
from pathlib import Path
import numpy as np

from lukefi.metsi.domain.natural_processes.motti_dll_wrapper import (
    Motti4DLL,
    GrowthDeltas,
)
from lukefi.metsi.data.enums.internal import (
    TreeSpecies,
    CONIFEROUS_SPECIES,
    DECIDUOUS_SPECIES,
)
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.vector_model import ReferenceTrees
from lukefi.metsi.domain.natural_processes.util import update_stand_growth_vectorized
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.data.layered_model import PossiblyLayered


def _species_to_motti(spe: int) -> int:
    """
    Map internal TreeSpecies -> Motti species codes directly.
    - Keep main species 1..5 as-is
    - Collapse both alders (GREY_ALDER, COMMON_ALDER) to 6
    - If in CONIFEROUS_SPECIES -> 8
    - If in DECIDUOUS_SPECIES -> 9
    """
    ts = TreeSpecies(int(spe))
    if ts in (TreeSpecies.PINE, TreeSpecies.SPRUCE,
              TreeSpecies.SILVER_BIRCH, TreeSpecies.DOWNY_BIRCH,
              TreeSpecies.ASPEN):
        return int(ts)
    if ts in (TreeSpecies.GREY_ALDER, TreeSpecies.COMMON_ALDER):
        return int(TreeSpecies.GREY_ALDER)  # Motti uses a single Alder code (6)
    if ts in CONIFEROUS_SPECIES:
        return int(TreeSpecies.OTHER_CONIFEROUS)  # 8
    if ts in DECIDUOUS_SPECIES:
        return int(TreeSpecies.OTHER_DECIDUOUS)  # 9

    raise ValueError(f"Unsupported tree species code: {int(spe)}")


def auto_euref_km(y1: float, x1: float) -> tuple[float, float]:
    """
    Normalize to EUREF-FIN/TM35FIN kilometers.
    Input is expected to be in meters
    - Raise if values look like lat/long.
    """
    abs_y, abs_x = abs(y1), abs(x1)

    # Clear lat/long guard
    if abs_y <= 90.0 and abs_x <= 180.0:
        raise ValueError(
            f"Coordinates look like lat/long (Y={y1}, X={x1}). "
            "Expected EUREF-FIN/TM35 in kilometers."
        )

    return y1 / 1000.0, x1 / 1000.0


def _spedom(rt: ReferenceTrees) -> int | None:
    """
    Dominant species from SoA data (Motti species code).
    Prefer basal area totals; if BA totals are all zero/missing, fall back to stems/ha.
    """
    if rt is None:
        return None
    n = rt.size
    if n == 0:
        return None

    # Convert species to Motti codes (will raise if invalid)
    spe_codes = np.asarray([_species_to_motti(int(s)) for s in rt.species.tolist()], dtype=int)

    # Basal area per tree: stems_per_ha * π * (0.5 * d_cm * 0.01 m/cm)^2
    d_cm = np.nan_to_num(rt.breast_height_diameter, nan=0.0)
    f_ha = np.nan_to_num(rt.stems_per_ha, nan=0.0)
    ba_per_tree = f_ha * np.pi * (0.5 * d_cm * 0.01) ** 2  # m²/ha contribution

    # Sum BA per species code
    per: Dict[int, float] = {}
    for code, ba in zip(spe_codes.tolist(), ba_per_tree.tolist()):
        per[code] = per.get(code, 0.0) + float(ba)

    use_basal = any(v > 0.0 for v in per.values())
    if not use_basal:
        per.clear()
        # Fallback: stems/ha totals per species
        for code, stems in zip(spe_codes.tolist(), f_ha.tolist()):
            per[code] = per.get(code, 0.0) + float(stems)

    if not per:
        return None

    return max(per.items(), key=lambda kv: kv[1])[0]



# -------- vectorized predictor --------

class MottiDLLPredictorVec:
    """
    SoA-based predictor feeding the Motti DLL. Builds C tree buffers from vector arrays.
    """

    def __init__(
        self,
        stand: PossiblyLayered[ForestStand],
        data_dir: Optional[str] = None,
        use_dll_site_convert: bool = True,
        dll: Optional["Motti4DLL"] = None,
    ) -> None:
        self.stand = stand
        self.use_dll_site_convert = use_dll_site_convert

        if dll is not None:
            self.dll = dll
        else:
            if data_dir is None:
                raise ValueError("data_dir must be provided (directory containing the Motti library).")
            self.dll = Motti4DLL(_resolve_shared_object(data_dir), data_dir=data_dir)

    # ---- stand/site properties ----
    @property
    def year(self) -> float:
        return float(getattr(self.stand, "year", None) or 2010.0)

    @property
    def get_y(self) -> float:
        return float(self.stand.geo_location[0])

    @property
    def get_x(self) -> float:
        return float(self.stand.geo_location[1])

    @property
    def get_z(self) -> float:
        z = self.stand.geo_location[2]
        return float(z if z not in (None, 0.0) else -1.0)  # let DLL infer if missing

    @property
    def lake(self) -> float:
        return float(getattr(self.stand, "lake_effect", 0.0) or 0.0)

    @property
    def sea(self) -> float:
        return float(getattr(self.stand, "sea_effect", 0.0) or 0.0)

    @property
    def mal(self) -> int:
        return int(self.stand.land_use_category)

    @property
    def mty(self) -> int:
        return int(self.stand.site_type_category)

    @property
    def alr(self) -> int:
        return int(self.stand.soil_peatland_category)

    @property
    def verl(self) -> int:
        return int(self.stand.tax_class)

    @property
    def verlt(self) -> int:
        return int(self.stand.tax_class_reduction)

    # ---- evolve ----

    def evolve(self, step: int = 5, sim_year: int = 0) -> GrowthDeltas:
        rt = self.stand.reference_trees_soa
        if not rt:
            return GrowthDeltas(tree_ids=[], trees_id=[], trees_ih=[], trees_if=[])
        n = rt.size
        if n == 0:
            # nothing to do; fake zeros in the same shape the caller expects
            return GrowthDeltas(tree_ids=[], trees_id=[], trees_ih=[], trees_if=[])

        spedom = _spedom(self.stand.reference_trees_soa)

        # site (DLL converts site index if asked)
        y_km, x_km = auto_euref_km(self.get_y, self.get_x)
        site = self.dll.new_site(
            Y=y_km,
            X=x_km,
            Z=self.get_z,
            lake=self.lake,
            sea=self.sea,
            mal=self.mal,
            mty=self.mty,
            verl=self.verl,
            verlt=self.verlt,
            alr=self.alr,
            year=sim_year,
            step=step,
            convert_mela_site=self.use_dll_site_convert,
            spedom=spedom,
            spedom2=spedom,
            nstorey=1.0,
            gstorey=1.0,
        )

        # Build trees buffer from SoA
        # ids are stable 1..n in current order
        ids = np.arange(1, n + 1, dtype=int)

        # Prepare vectors (with NaN -> 0 for DLL)
        stems = np.nan_to_num(rt.stems_per_ha, nan=0.0)
        d13 = np.nan_to_num(rt.breast_height_diameter, nan=0.0)
        h = np.nan_to_num(rt.height, nan=0.0)
        age = np.nan_to_num(rt.biological_age, nan=0.0)
        age13 = np.nan_to_num(rt.breast_height_age, nan=0.0)
        cr = np.nan_to_num(getattr(rt, "crown_ratio", np.zeros(n, dtype=float)), nan=0.0)
        origin = np.nan_to_num(getattr(rt, "origin", np.zeros(n, dtype=float)), nan=0.0)

        # Species conversion (raises on invalid)
        spe_vec = np.asarray([_species_to_motti(int(s)) for s in rt.species.tolist()], dtype=int)

        # Build list[dict] for the DLL (fields used by wrapper)
        trees_py = [
            {
                "id": int(i),
                "f": float(f),
                "d13": float(d),
                "h": float(hh),
                "spe": int(sp),
                "age": float(a),
                "age13": float(a13),
                "cr": float(c),
                "snt": int(o + 1),
            }
            for i, f, d, hh, sp, a, a13, c, o in zip(
                ids.tolist(),
                stems.tolist(),
                d13.tolist(),
                h.tolist(),
                spe_vec.tolist(),
                age.tolist(),
                age13.tolist(),
                cr.tolist(),
                origin.astype(int).tolist(),
            )
        ]

        yp, _n = self.dll.new_trees(trees_py)
        return self.dll.grow(site, yp, _n, step=step, ctrl=None, skip_init=True)


# -------- DLL path resolver (same behavior as AoS helper) --------

def _resolve_shared_object(p: Union[str, Path]) -> Path:
    """
    Resolve a Motti shared library inside a directory, or pass through an exact file path.
    Raises ValueError if p is None. Returns a Path (may be a directory if nothing matched).
    """
    if p is None:
        raise ValueError("data_dir must be provided (directory containing the Motti library).")

    p = Path(p)

    if p.is_file():
        return p

    candidates: Iterable[str] = (
        # Windows
        "mottisc.dll", "mottiue.dll",
        # Linux
        "libmottisc.so", "libmottiue.so", "mottisc.so", "mottiue.so",
    )
    for name in candidates:
        cand = p / name
        if cand.exists():
            return cand

    # No match found; return directory so downstream can raise a clear error when loading.
    return p


# -------- public API --------

def species_to_motti(x: int) -> int:
    return _species_to_motti(x)


def grow_motti_dll_vec(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    """
    Vector-only Motti grow:
      - Requires stand.reference_trees_soa
      - Builds DLL input from SoA, runs growth, applies deltas vectorized
      - Prunes trees with stems_per_ha < 1.0 after update
    operation_parameters:
      - step: int (years), default 5
      - data_dir: path to folder/file for the Motti DLL (required unless a predictor is injected)
      - predictor: optional injected Motti4DLL wrapper (testing)
    """

    sim_year = input_[1].current_time_point or stand.year
    step = int(operation_parameters.get("step", 5))
    data_dir = operation_parameters.get("data_dir", None)
    predictor = operation_parameters.get("predictor", None)

    stand, collected_data = input_

    rt = stand.reference_trees_soa
    if rt is None:
        raise ValueError("Reference trees not vectorized (stand.reference_trees_soa is None).")
    if rt.size == 0:
        return input_

    # Construct predictor
    if predictor is None:
        if data_dir is None:
            raise ModuleNotFoundError("data_dir must be provided (directory containing the Motti library).")
        pred = MottiDLLPredictorVec(stand, data_dir= data_dir)
    else:
        pred = predictor

    growth = pred.evolve(step= step, sim_year= sim_year)

    # Map deltas by returned IDs (subset of original if deaths occurred)
    id_to_delta_d = {int(i): float(d) for i, d in zip(growth.tree_ids, growth.trees_id)}
    id_to_delta_h = {int(i): float(h) for i, h in zip(growth.tree_ids, growth.trees_ih)}
    id_to_delta_f = {int(i): float(f) for i, f in zip(growth.tree_ids, growth.trees_if)}

    n = rt.size
    ids = np.arange(1, n + 1, dtype=int)

    base_d = np.nan_to_num(rt.breast_height_diameter, nan=0.0)
    base_h = np.nan_to_num(rt.height, nan=0.0)
    base_f = np.nan_to_num(rt.stems_per_ha, nan=0.0)

    # Build updated arrays in the original order:
    # - If ID present in DLL result: add deltas
    # - If missing: stems -> 0 (dead/removed), keep d/h unchanged
    d_new = base_d.copy()
    h_new = base_h.copy()
    f_new = base_f.copy()

    for idx, tid in enumerate(ids.tolist()):
        if tid in id_to_delta_d:
            d_new[idx] = base_d[idx] + id_to_delta_d[tid]
            h_new[idx] = base_h[idx] + id_to_delta_h[tid]
            f_new[idx] = max(base_f[idx] + id_to_delta_f[tid], 0.0)
        else:
            f_new[idx] = 0.0

    # Apply vectorized update (also advances ages etc. inside util)
    update_stand_growth_vectorized(stand, d_new, h_new, f_new, step)

    return stand, collected_data
