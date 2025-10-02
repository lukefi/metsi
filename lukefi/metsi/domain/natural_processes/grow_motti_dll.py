from pathlib import Path
from typing import Optional, Union, Iterable, Tuple, Mapping, Dict
from functools import cached_property
from types import MappingProxyType

from lukefi.metsi.forestry.forestry_utils import (
    calculate_basal_area,
    overall_basal_area,
)

from lukefi.metsi.domain.natural_processes.motti_dll_wrapper import (
    Motti4DLL,
    GrowthDeltas
)

from lukefi.metsi.data.enums.internal import (
    TreeSpecies,
    CONIFEROUS_SPECIES,
    DECIDUOUS_SPECIES,
)
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.natural_processes.util import update_stand_growth
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.data.layered_model import PossiblyLayered


def _spedom(stand) -> int:
    """
    Pick dominant species.
    Prefer basal area totals; if BA totals are all zero/missing, fall back to stems/ha.
    Returns dominant species as Mottispecies codes.
    """
    # 1) Try basal area first
    use_basal = overall_basal_area(stand.reference_trees) > 0.0
    per: Dict[int, float] = {}

    if use_basal:
        # group BA by Motti species code
        for t in stand.reference_trees:
            motti = species_to_motti(int(t.species))
            per[motti] = per.get(motti, 0.0) + float(calculate_basal_area(t) or 0.0)

        # if everything was zero (e.g., no diameters), fall back to stems
        if sum(per.values()) == 0.0:
            use_basal = False
            per.clear()

    # 2) Fallback: stems/ha
    if not use_basal:
        for t in stand.reference_trees:
            motti = species_to_motti(int(t.species))
            per[motti] = per.get(motti, 0.0) + float(t.stems_per_ha or 0.0)

    if not per:
        return TreeSpecies.PINE

    # 3) Choose top-1
    return max(per.items(), key=lambda kv: kv[1])[0]


def _resolve_shared_object(p: Union[str, Path]) -> Path:
    """
    Resolve a Motti shared library inside a directory, or pass through an exact file path.
    Raises ValueError if p is None. Returns a Path (may be a directory if nothing matched).
    """
    if p is None:
        raise ValueError("data_dir must be provided (directory containing the Motti library).")

    p = Path(p)

    # If a direct file path is given, just return it (caller/dlopen will validate existence).
    if p.is_file():
        return p

    # If it's a directory, search typical candidates.
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





class MottiDLLPredictor:
    def __init__(
        self,
        stand: PossiblyLayered[ForestStand],
        data_dir: Optional[str] = None,
        use_dll_species_convert: bool = True,
        use_dll_site_convert: bool = True,
        dll: Optional["Motti4DLL"] = None,  # <-- NEW: injectable DLL for tests
    ):
        self.stand = stand

        if dll is not None:
            # Test/DI path: no filesystem, no dlopen
            self.dll = dll
        else:
            # Prod path: resolve from folder (data_dir must be provided)
            if data_dir is None:
                raise ValueError("data_dir must be provided (directory containing the Motti library).")
            resolved = _resolve_shared_object(data_dir)
            self.dll = Motti4DLL(resolved, data_dir=data_dir)

        self.use_dll_species_convert = use_dll_species_convert
        self.use_dll_site_convert = use_dll_site_convert

    @property
    def year(self) -> float:
        y = getattr(self.stand, "year", None)
        return float(y) if y is not None else 2010.0

    @property
    def get_y(self) -> float | None:
        if self.stand and self.stand.geo_location:
            return self.stand.geo_location[0]
        return None

    @property
    def get_x(self) -> float | None:
        if self.stand and self.stand.geo_location:
            return self.stand.geo_location[1]
        return None

    @property
    def get_z(self) -> float:
        if self.stand and self.stand.geo_location:
            z = self.stand.geo_location[2]
            if z is None or z == 0.0:
                return -1.0
            return float(z)
        return -1.0

    @property
    def lake(self) -> float:
        v = getattr(self.stand, "lake_effect", 0.0)
        return float(v if v is not None else 0.0)

    @property
    def sea(self) -> float:
        v = getattr(self.stand, "sea_effect", 0.0)
        return float(v if v is not None else 0.0)

    @property
    def mal(self) -> int:
        luc = getattr(self.stand, "land_use_category", None)
        return int(luc.value) if luc is not None else 0

    @property
    def mty(self) -> int:
        st = getattr(self.stand, "site_type_category", None)
        return int(st.value) if st is not None else 0

    @property
    def alr(self) -> int:
        s = getattr(self.stand, "soil_peatland_category", None)
        return int(s.value) if s is not None else 0

    @property
    def verl(self) -> int:
        v = getattr(self.stand, "tax_class", None)
        return int(v) if v is not None else 0

    @property
    def verlt(self) -> int:
        v = getattr(self.stand, "tax_class_reduction", None)
        return int(v) if v is not None else 0


    @cached_property
    def _trees_py(self) -> list[dict]:
        trees = []
        for idx, t in enumerate(self.stand.reference_trees):

            spe = species_to_motti(int(t.species or 0))

            tid = int((getattr(t, "tree_number", None) or (idx + 1)))
            trees.append({
                "id": tid,
                "f": float(t.stems_per_ha or 0.0),
                "d13": float(t.breast_height_diameter or 0.0),
                "h": float(t.height or 0.0),
                "spe": int(spe),
                "age": float(t.biological_age or 0.0),
                "age13": float(t.breast_height_age or 0.0),
                "cr": float(getattr(t, "crown_ratio", 0.0) or 0.0),
                "snt": int((t.origin or 0) + 1),
            })
        return trees

    @property
    def trees(self) -> Tuple[Mapping, ...]:
        # read-only snapshot to avoid accidental mutation in callers/tests
        return tuple(MappingProxyType(d) for d in self._trees_py)

    def evolve(self, step: int = 5) -> GrowthDeltas:
        dominant_species = _spedom(self.stand)
        y_km, x_km = auto_euref_km(self.get_y, self.get_x)
        site = self.dll.new_site(
            Y=y_km, X=x_km, Z=self.get_z,
            lake=self.lake, sea=self.sea,
            mal=self.mal,
            mty=self.mty,
            verl=self.verl, verlt=self.verlt, alr=self.alr,
            year=self.year, step=step,
            spedom=dominant_species,
            spedom2=dominant_species,
            nstorey=1.0,
            gstorey=1.0,
            convert_mela_site=self.use_dll_site_convert,
        )
        trees, n = self.dll.new_trees(self._trees_py)
        return self.dll.grow(site, trees, n, step=step, ctrl=None, skip_init=True)



def auto_euref_km(y1: float | None, x1: float | None) -> tuple[float, float]:
    """
    Normalize to EUREF-FIN/TM35FIN kilometers.
    Input is expected to be in meters
    - Raise if values look like lat/long.
    """
    if not y1 or not x1:
        return 0.0, 0.0
    abs_y, abs_x = abs(y1), abs(x1)

    # Clear lat/long guard
    if abs_y <= 90.0 and abs_x <= 180.0:
        raise ValueError(
            f"Coordinates look like lat/long (Y={y1}, X={x1}). "
            "Expected EUREF-FIN/TM35 in kilometers."
        )

    return y1 / 1000.0, x1 / 1000.0


def species_to_motti(spe: int | None) -> int:
    """
    Map internal TreeSpecies -> Motti species codes directly.
    - Keep main species 1..5 as-is
    - Collapse both alders (GREY_ALDER, COMMON_ALDER) to 6
    - If in CONIFEROUS_SPECIES -> 8
    - If in DECIDUOUS_SPECIES -> 9
    """
    if not spe:
        return TreeSpecies.PINE
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

def grow_motti_dll(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    """
    Evolves the stand by `step` years. If no predictor is provided and `data_dir` is None,
    this is treated as a no-op (DLL not available).
    """
    step = int(operation_parameters.get("step", 5))
    data_dir = operation_parameters.get("data_dir", None)
    predictor = operation_parameters.get("predictor", None)

    stand, collected_data = input_

    # If a predictor is supplied (e.g., from tests), use it, regardless of data_dir.
    if predictor is None:
        # No injected predictor. If DLL path isn't provided, raise an error
        if data_dir is None:
            raise ModuleNotFoundError("data_dir must be provided (directory containing the Motti library).")

        # Production path: construct predictor from data_dir.
        pred = MottiDLLPredictor(stand, data_dir=data_dir)
    else:
        pred = predictor

    for idx, t in enumerate(stand.reference_trees, start=1):
        t.tree_number = idx


    growth = pred.evolve(step=step)

    id_to_delta_d  = {int(i): d for i, d in zip(growth.tree_ids, growth.trees_id)}
    id_to_delta_h  = {int(i): h for i, h in zip(growth.tree_ids, growth.trees_ih)}
    id_to_delta_f  = {int(i): f for i, f in zip(growth.tree_ids, growth.trees_if)}

    diameters, heights, stems = [], [], []
    for t in stand.reference_trees:
        tid = int(getattr(t, "tree_number", 0))
        if tid in id_to_delta_d:
            diameters.append((t.breast_height_diameter or 0.0) + id_to_delta_d[tid])
            heights.append((t.height or 0.0) + id_to_delta_h[tid])
            stems.append(max((t.stems_per_ha or 0.0) + id_to_delta_f[tid], 0.0))
        else:
            # Not returned by DLL -> treat as dead/removed
            diameters.append(t.breast_height_diameter or 0.0)
            heights.append(t.height or 0.0)
            stems.append(0.0)

    update_stand_growth(stand, diameters, heights, stems, step)
    return stand, collected_data
