from __future__ import annotations
from pathlib import Path
from typing import Optional, Union, Iterable,  Tuple, Dict, Mapping
from dataclasses import dataclass
from functools import cached_property
from collections import defaultdict
from types import MappingProxyType

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
    return int(TreeSpecies.OTHER_DECIDUOUS)  # sensible fallback

def _dominant_species_codes(stand) -> Dict[str, int]:
    """
    Pick dominant and sub-dominant species by stems/ha.
    Returns 'spedom' and 'spedom2' as *Motti* species codes (no Mela step).
    """
    per = defaultdict(float)
    for t in stand.reference_trees:
        s_motti = _species_to_motti(int(t.species))
        per[s_motti] += float(t.stems_per_ha or 0.0)

    if not per:
        return {"spedom": 1, "spedom2": 2}
    ordered = sorted(per.items(), key=lambda kv: kv[1], reverse=True)
    top1 = ordered[0][0]
    top2 = ordered[1][0] if len(ordered) > 1 else (2 if top1 == 1 else 1)
    return {"spedom": top1, "spedom2": top2}

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
        stand,
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
    def year(self) -> Optional[float]:
        return getattr(self.stand, "year", None) or 2010.0
    @property
    def get_y(self) -> float:
        return self.stand.geo_location[0]
    @property
    def get_x(self) -> float:
        return self.stand.geo_location[1]
    @property
    def get_z(self) -> float:
        z = self.stand.geo_location[2]
        return float(z if z not in (None, 0.0) else -1.0)  # let DLL infer if missing
    @property
    def lake(self) -> float:
        return getattr(self.stand, "lake_effect", 0.0)
    @property
    def sea(self) -> float:
        return getattr(self.stand, "sea_effect", 0.0)
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

    @cached_property
    def _trees_py(self) -> list[dict]:
        trees = []
        for idx, t in enumerate(self.stand.reference_trees):

            spe = _species_to_motti(int(t.species))
            tid = int((getattr(t, "tree_number", None) or (idx + 1)))
            trees.append(dict(
                id=tid,
                f=float(t.stems_per_ha or 0.0),
                d13=float(t.breast_height_diameter or 0.0),
                h=float(t.height or 0.0),
                spe=int(spe),
                age=float(t.biological_age or 0.0),
                age13=float(t.breast_height_age or 0.0),
                cr=float(getattr(t, "crown_ratio", 0.0) or 0.0),
                snt=int((t.origin or 0) + 1),
            ))
        return trees

    @property
    def trees(self) -> Tuple[Mapping, ...]:
        # read-only snapshot to avoid accidental mutation in callers/tests
        return tuple(MappingProxyType(d) for d in self._trees_py)

    def evolve(self, step: int = 5) -> GrowthDeltas:
        dom = _dominant_species_codes(self.stand)
        site = self.dll.new_site(
            Y=self.get_y, X=self.get_x, Z=self.get_z,
            lake=self.lake, sea=self.sea,
            mal=self.mal,
            mty=self.mty,
            verl=self.verl, verlt=self.verlt, alr=self.alr,
            year=self.year, step=step,
            convert_coords=True,
            overrides={
                "spedom": int(dom["spedom"]),
                "spedom2": int(dom["spedom2"]),
                "nstorey": 1, "gstorey": 1,
            },
            convert_mela_site=self.use_dll_site_convert,
        )
        trees, n = self.dll.new_trees(self._trees_py)
        return self.dll.grow(site, trees, n, step=step, ctrl=None, skip_init=True)


def grow_motti_dll(input_: Tuple["ForestStand", None], /, **operation_parameters) -> Tuple["ForestStand", None]:
    """
    Evolves the stand by `step` years. If no predictor is provided and `data_dir` is None,
    this is treated as a no-op (DLL not available).
    """
    step = int(operation_parameters.get("step", 5))
    data_dir = operation_parameters.get("data_dir", None)
    predictor = operation_parameters.get("predictor", None)  # <-- NEW

    stand, _ = input_

    # If a predictor is supplied (e.g., from tests), use it, regardless of data_dir.
    if predictor is None:
        # No injected predictor. If DLL path isn't provided, do nothing safely.
        if data_dir is None:
            return stand, None

        # Production path: construct predictor from data_dir. This will still
        # raise if data_dir is invalid/missing libs, preserving the original behavior.
        pred = MottiDLLPredictor(stand, data_dir=data_dir)
    else:
        pred = predictor

    # Assign stable integer ids before evolving (unchanged logic)
    #for idx, t in enumerate(stand.reference_trees, start=1):
    #    t.id = str(idx)

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
            diameters.append(t.breast_height_diameter)
            heights.append(t.height)
            stems.append(0.0)

    update_stand_growth(stand, diameters, heights, stems, step)
    #stand.reference_trees = [t for t in stand.reference_trees if (t.stems_per_ha is not None and t.stems_per_ha >= 1.0)]
    return stand, None
