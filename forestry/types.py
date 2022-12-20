from dataclasses import dataclass
from forestry.biomass_repola import BiomassData


@dataclass
class VolumeAggregate:
    growth_volume: float
    current_volume: float

    @classmethod
    def initial(cls, vol: float) -> "VolumeAggregate":
        return cls(0, vol)

    @classmethod
    def from_prev(cls, prev: "VolumeAggregate", vol: float) -> "VolumeAggregate":
        return cls(prev.growth_volume+vol-prev.current_volume, vol)


@dataclass
class BiomassAggregate:
    difference: BiomassData
    current: BiomassData

    @classmethod
    def initial(cls, bm: BiomassData) -> "BiomassAggregate":
        return cls(BiomassData(), bm)

    @classmethod
    def from_prev(cls, prev: "BiomassAggregate", bm: BiomassData) -> "BiomassAggregate":
        return cls(prev.difference+bm-prev.current, bm)
