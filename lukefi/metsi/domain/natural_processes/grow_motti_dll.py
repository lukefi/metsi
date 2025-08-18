from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import List, Tuple, Optional, Dict
from collections import defaultdict
from pathlib import Path
# Adjust import to your project structure if needed
from lukefi.metsi.domain.natural_processes.pymotti_dll_wrapper import Motti4DLL

from typing import TYPE_CHECKING

try:
    from lukefi.metsi.data.conversion import internal2mela
    from lukefi.metsi.data.enums.internal import TreeSpecies
    from lukefi.metsi.data.model import ForestStand
    from lukefi.metsi.domain.natural_processes.util import update_stand_growth  # -> None
except ImportError:
    # If importing ForestStand also fails during runtime, you can gate it for type-checkers only:
    if TYPE_CHECKING:
        from lukefi.metsi.data.model import ForestStand  # for hints only


def _mela_species(spe: int) -> int:
    if internal2mela is None:
        return int(spe)
    code = internal2mela.species_map[TreeSpecies(spe)].value
    return code


def _dominant_species_codes(stand) -> Dict[str, int]:
    """
    Pick dominant and sub-dominant species by stems/ha.
    Returns dict with 'spedom' and 'spedom2' in *MELA* codes; DLL wrapper converts further.
    """
    per = defaultdict(float)
    for t in stand.reference_trees:
        try:
            s = int(t.species)
            mela = _mela_species(s)
            per[mela] += float(t.stems_per_ha or 0.0)
        except Exception:
            pass
    if not per:
        return {"spedom": 1, "spedom2": 2}
    ordered = sorted(per.items(), key=lambda kv: kv[1], reverse=True)
    top1 = ordered[0][0]
    top2 = ordered[1][0] if len(ordered) > 1 else (2 if top1 == 1 else 1)
    return {"spedom": top1, "spedom2": top2}


@dataclass
class _PredictLike:
    ids: list[float]
    trees_id: List[float]
    trees_ih: List[float]
    trees_if: List[float]


class MottiDLLPredictor:
    def __init__(
        self,
        stand,
        dll_path: str = "mottisc.dll",
        data_dir: Optional[str] = None,
        use_dll_species_convert: bool = True,
        use_dll_site_convert: bool = True,
    ):

        self.stand = stand
        self.dll = Motti4DLL(dll_path, data_dir=data_dir)
        self.use_dll_species_convert = use_dll_species_convert
        self.use_dll_site_convert = use_dll_site_convert

    @property
    def year(self) -> Optional[float]: return getattr(self.stand, "year", None) or 2010.0
    @property
    def Y(self) -> float: return self.stand.geo_location[0]
    @property
    def X(self) -> float: return self.stand.geo_location[1]
    @property
    def Z(self) -> float:
        z = self.stand.geo_location[2]
        return float(z if z not in (None, 0.0) else -1.0)  # let DLL infer if missing
    @property
    def lake(self) -> float: return getattr(self.stand, "lake_effect", 0.0)
    @property
    def sea(self) -> float: return getattr(self.stand, "sea_effect", 0.0)
    @property
    def mal(self) -> int: return int(self.stand.land_use_category)
    @property
    def mty(self) -> int: return int(self.stand.site_type_category)
    @property
    def alr(self) -> int: return int(self.stand.soil_peatland_category)
    @property
    def verl(self) -> int: return int(self.stand.tax_class)
    @property
    def verlt(self) -> int: return int(self.stand.tax_class_reduction)

    @cached_property
    def _trees_py(self) -> list[dict]:
        trees = []
        for idx, t in enumerate(self.stand.reference_trees):
            mela_spe = _mela_species(int(t.species))
            spe = self.dll.convert_species_code(mela_spe) if self.use_dll_species_convert else mela_spe
            trees.append(dict(
                id=float(getattr(t, "id", idx + 1)),
                f=float(t.stems_per_ha or 0.0),
                d13=float((t.breast_height_diameter or 0.0)),
                h=float((t.height or 0.0)),
                spe=int(spe),
                age=float(t.biological_age or 0.0),
                age13=float((t.breast_height_age or 0.0)),
                cr=float(getattr(t, "crown_ratio", 0.4) or 0.4),
                snt=int((t.origin or 0) + 1)
            ))
        return trees

    def evolve(self, step: int = 5) -> _PredictLike:
        dom = _dominant_species_codes(self.stand)
        site = self.dll.new_site(
            Y=self.Y, X=self.X, Z=self.Z,
            lake=self.lake, sea=self.sea,
            mal=self.mal,
            mty=(self.dll.convert_site_index(self.mty) if self.use_dll_site_convert else self.mty),
            verl=self.verl, verlt=self.verlt, alr=self.alr,
            year=self.year, step=step,
            convert_coords=True,
            overrides={
                "spedom": self.dll.convert_species_code(dom["spedom"]),
                "spedom2": self.dll.convert_species_code(dom["spedom2"]),
                "nstorey": 1, "gstorey": 1,
            }
        )
        trees, n = self.dll.new_trees(self._trees_py)
        deltas = self.dll.grow(site, trees, n, step=step, ctrl=None, skip_init=True)  # death_tree=1 inside
        return _PredictLike(deltas.tree_ids, deltas.trees_id, deltas.trees_ih, deltas.trees_if)


def grow_motti_dll(input_: Tuple["ForestStand", None], /, **operation_parameters) -> Tuple["ForestStand", None]:
    """
    Evolves the stand by `step` years. Mirrors the C wrapper’s call sequence and policies.
    """
    step = int(operation_parameters.get("step", 5))
    dll_path = operation_parameters.get("dll_path", "mottisc.dll")
    data_dir = operation_parameters.get("data_dir", None)

    stand, _ = input_
    # Ensure stable per-tree IDs that match what we pass to the DLL
    for idx, t in enumerate(stand.reference_trees, start=1):
        tid = getattr(t, "id", None)
        if not isinstance(tid, (int, float)) or tid == 0:
            try:
                t.id = float(idx)
            except Exception:
                pass

    for idx, t in enumerate(stand.reference_trees, start=1):
        tid = getattr(t, "id", None)
        if not isinstance(tid, (int, float)) or tid <= 0:
            t.id = float(idx)

    pred = MottiDLLPredictor(stand, dll_path=dll_path, data_dir=data_dir)
    growth = pred.evolve(step=step)

    id_to_delta_d  = {int(round(i)): d for i, d in zip(growth.ids,  growth.trees_id)}
    id_to_delta_h  = {int(round(i)): h for i, h in zip(growth.ids,  growth.trees_ih)}
    id_to_delta_f  = {int(round(i)): f for i, f in zip(growth.ids,  growth.trees_if)}


    diameters, heights, stems = [], [], []
    for t in stand.reference_trees:
        tid = int(round(float(getattr(t, "id", 0.0))))
        if tid in id_to_delta_d:
            diameters.append(t.breast_height_diameter + id_to_delta_d[tid])
            heights.append(t.height + id_to_delta_h[tid])
            stems.append(t.stems_per_ha + id_to_delta_f[tid])
        else:
            # Not returned by DLL -> treat as dead/removed (C wrapper sets stems=0 then packs)
            diameters.append(t.breast_height_diameter)
            heights.append(t.height)
            stems.append(0.0)

    update_stand_growth(stand, diameters, heights, stems, step)
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None