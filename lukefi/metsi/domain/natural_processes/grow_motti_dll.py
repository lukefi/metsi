
from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import List, Tuple

from lukefi.metsi.domain.natural_processes.pymotti_dll_wrapper import Motti4DLL

try:
    from lukefi.metsi.data.conversion import internal2mela
    from lukefi.metsi.data.enums.internal import TreeSpecies
    from lukefi.metsi.data.model import ForestStand
    from lukefi.metsi.domain.natural_processes.util import update_stand_growth
except Exception:
    internal2mela = None
    TreeSpecies = None
    ForestStand = None
    def update_stand_growth(*args, **kwargs): raise RuntimeError("update_stand_growth not available")

def spe2motti(spe: int) -> int:
    if internal2mela is None:
        return int(spe)
    code = internal2mela.species_map[TreeSpecies(spe)].value
    return code if code <= 6 else code + 1

@dataclass
class _PredictLike:
    trees_id: List[float]
    trees_ih: List[float]
    trees_if: List[float]

class MottiDLLPredictor:
    def __init__(self, stand, dll_path: str = "mottisc.dll", data_dir: str | None = None):
        self.stand = stand
        self.dll = Motti4DLL(dll_path, data_dir=data_dir)

    @property
    def year(self) -> float: return self.stand.year
    @property
    def Y(self) -> float: return self.stand.geo_location[0]
    @property
    def X(self) -> float: return self.stand.geo_location[1]
    @property
    def Z(self) -> float: return self.stand.geo_location[2]
    @property
    def dd(self) -> float: return self.stand.degree_days
    @property
    def lake(self) -> float: return self.stand.lake_effect
    @property
    def sea(self) -> float: return self.stand.sea_effect
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
        for t in self.stand.reference_trees:
            trees.append(dict(
                f=float(t.stems_per_ha or 0.0),
                d13=float((t.breast_height_diameter or 0.0)),
                h=float((t.height or 0.0)),
                spe=int(spe2motti(t.species)),
                age=float(t.biological_age or 0.0),
                age13=float((t.breast_height_age or 0.0)),
                cr=float(getattr(t, "crown_ratio", 0.4) or 0.4),
                snt=int((t.origin or 0) + 1)
            ))
        return trees

    def evolve(self, step: int = 5) -> _PredictLike:
        site = self.dll.new_site(Y=self.Y, X=self.X, Z=self.Z, dd=self.dd,
                                 lake=self.lake, sea=self.sea,
                                 mal=self.mal, mty=self.mty, verl=self.verl, verlt=self.verlt, alr=self.alr,
                                 year=self.year, step=step)
        trees, n = self.dll.new_trees(self._trees_py)
        deltas = self.dll.grow(site, trees, n, step=step)
        return _PredictLike(deltas.trees_id, deltas.trees_ih, deltas.trees_if)


def grow_motti_dll(input_: Tuple["ForestStand", None], /, **operation_parameters) -> Tuple["ForestStand", None]:
    step = int(operation_parameters.get("step", 5))
    dll_path = operation_parameters.get("dll_path", "mottisc.dll")
    data_dir = operation_parameters.get("data_dir", None)
    stand, _ = input_
    pred = MottiDLLPredictor(stand, dll_path=dll_path, data_dir=data_dir)
    growth = pred.evolve(step=step)

    diameters = [t.breast_height_diameter + d for t, d in zip(stand.reference_trees, growth.trees_id)]
    heights   = [t.height + h for t, h in zip(stand.reference_trees, growth.trees_ih)]
    stems     = [t.stems_per_ha + df for t, df in zip(stand.reference_trees, growth.trees_if)]

    update_stand_growth(stand, diameters, heights, stems, step)
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
