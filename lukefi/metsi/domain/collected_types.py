from dataclasses import dataclass
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.app.utils import MetsiException


@dataclass
class BiomassData:
    time_point: int | None = None
    stem_wood: float = 0.0
    stem_bark: float = 0.0
    stem_waste: float = 0.0
    living_branches: float = 0.0
    dead_branches: float = 0.0
    foliage: float = 0.0
    stumps: float = 0.0
    roots: float = 0.0

    def total(self):
        return sum([
            self.stem_wood,
            self.stem_bark,
            self.stem_waste,
            self.living_branches,
            self.dead_branches,
            self.foliage,
            self.stumps,
            self.roots
        ])

    def __add__(self, other):
        return self.__radd__(other)

    def __radd__(self, other: 'BiomassData | float | int'):
        if isinstance(other, (float, int)):
            return BiomassData(
                stem_wood=self.stem_wood + other,
                stem_bark=self.stem_bark + other,
                stem_waste=self.stem_waste + other,
                living_branches=self.living_branches + other,
                dead_branches=self.dead_branches + other,
                foliage=self.foliage + other,
                stumps=self.stumps + other,
                roots=self.roots + other
            )
        elif isinstance(other, BiomassData):
            return BiomassData(
                stem_wood=self.stem_wood + other.stem_wood,
                stem_bark=self.stem_bark + other.stem_bark,
                stem_waste=self.stem_waste + other.stem_waste,
                living_branches=self.living_branches + other.living_branches,
                dead_branches=self.dead_branches + other.dead_branches,
                foliage=self.foliage + other.foliage,
                stumps=self.stumps + other.stumps,
                roots=self.roots + other.roots
            )
        else:
            raise MetsiException(f"Can only do addition between numbers and BiomassData, not {type(other)}")

    def __sub__(self, other):
        return self + (other * - 1)

    def __mul__(self, factor):
        return self.__rmul__(factor)

    def __rmul__(self, factor):
        if not isinstance(factor, (int, float)):
            raise MetsiException(f"Can multiply BiomassData only with float or int, not {type(factor)}")
        return BiomassData(
            stem_wood=self.stem_wood * factor,
            stem_bark=self.stem_bark * factor,
            stem_waste=self.stem_waste * factor,
            living_branches=self.living_branches * factor,
            dead_branches=self.dead_branches * factor,
            foliage=self.foliage * factor,
            stumps=self.stumps * factor,
            roots=self.roots * factor
        )


@dataclass
class CrossCutResult:
    species: TreeSpecies
    timber_grade: int
    volume_per_ha: float
    value_per_ha: float
    stand_area: float
    source: str
    operation: str
    time_point: int

    # what's the right word here? "real", "absolute", something else?
    def get_real_volume(self) -> float:
        return self.volume_per_ha * self.stand_area

    def get_real_value(self) -> float:
        return self.value_per_ha * self.stand_area


@dataclass
class CrossCuttableTree:
    stems_per_ha: float
    species: TreeSpecies
    breast_height_diameter: float
    height: float
    source: str
    operation: str
    time_point: int


@dataclass
class NPVResult:
    time_point: int
    interest_rate: int
    value: float


@dataclass
class PriceableOperationInfo:
    operation: str
    units: float
    time_point: int

    def get_real_cost(self, unit_cost: float) -> float:
        return self.units * unit_cost
