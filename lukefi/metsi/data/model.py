import dataclasses
from typing import Optional, override
from dataclasses import dataclass
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.data.enums.internal import (LandUseCategory, OwnerCategory, SiteType, SoilPeatlandCategory,
                                              TreeSpecies, DrainageCategory, Storey)
from lukefi.metsi.data.enums.mela import MelaLandUseCategory
from lukefi.metsi.data.formats.util import convert_str_to_type as conv
from lukefi.metsi.data.layered_model import LayeredObject, PossiblyLayered
from lukefi.metsi.data.vector_model import ReferenceTrees, Strata
from lukefi.metsi.sim.finalizable import Finalizable

# NOTE:
# * the deepcopy methods here are roughly equivalent to
#       def __deepcopy__(self, memo):
#           return cls(**self.__dict__)
#   but __new__ + update() is ~25% faster (tested on Python 3.10).
#   dict.copy() vs dict(other) vs dict.update(other) are all equally fast.
# * none of the ForestStand / ReferenceTree / TreeStratum have their __init__
#   methods run when copied. don't add a (non-trivial) __init__ method to any class here.
# * if you add any containers on any class here, you need to add a manual copy
#   in the __deepcopy__ method. see ForestStand.__deepcopy__ for an example.


@dataclass(init=True, repr=False, order=False, unsafe_hash=False, frozen=False, match_args=False, kw_only=False,
           slots=False, weakref_slot=False, eq=False)
class TreeStratum():
    # VMI data type 2
    # SMK data type TreeStratum

    stand: Optional["ForestStand"] = None

    # identifier of the stratum within the container stand
    identifier: Optional[str] = None

    species: Optional[TreeSpecies] = None
    origin: Optional[int] = None
    stems_per_ha: Optional[float] = None  # stem count within a hectare
    mean_diameter: Optional[float] = None  # in decimeters
    mean_height: Optional[float] = None  # in meters
    # age in years when reached breast height
    breast_height_age: Optional[float] = None
    biological_age: Optional[float] = None  # age in years
    basal_area: Optional[float] = None  # stratum basal area
    saw_log_volume_reduction_factor: Optional[float] = None
    cutting_year: Optional[int] = None
    age_when_10cm_diameter_at_breast_height: Optional[int] = None
    tree_number: Optional[int] = None
    # Angle from plot origin, distance (m) to plot origin, height difference (m) with plot origin
    stand_origin_relative_position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    lowest_living_branch_height: Optional[float] = None
    management_category: Optional[int] = None
    # sapling stem count within a hectare
    sapling_stems_per_ha: Optional[float] = None
    sapling_stratum: bool = False  # this reference tree represents saplings
    storey: Optional[Storey] = None
    number_of_generated_trees: Optional[int] = None

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)

    def __deepcopy__(self, memo: dict) -> 'TreeStratum':
        s = TreeStratum.__new__(TreeStratum)
        s.__dict__.update(self.__dict__)
        return s

    def has_height(self):
        if self.mean_height is None:
            return False
        if self.mean_height > 0.0:
            return True
        return False

    def has_sapling_stems_per_ha(self) -> bool:
        if self.sapling_stems_per_ha is None:
            return False
        if self.sapling_stems_per_ha > 0.0:
            return True
        return False

    def has_stems_per_ha(self) -> bool:
        if self.stems_per_ha is None:
            return False
        if self.stems_per_ha > 0.0:
            return True
        return False

    def has_diameter(self) -> bool:
        if self.mean_diameter is None:
            return False
        if self.mean_diameter > 0.0:
            return True
        return False

    def has_breast_height_age(self) -> bool:
        if self.breast_height_age is None:
            return False
        if self.breast_height_age > 0.0:
            return True
        return False

    def has_biological_age(self) -> bool:
        if self.biological_age is None:
            return False
        if self.biological_age > 0.0:
            return True
        return False

    def has_basal_area(self) -> bool:
        if self.basal_area is None:
            return False
        if self.basal_area > 0.0:
            return True
        return False

    def has_height_over_130_cm(self) -> bool:
        if self.mean_height is None:
            return False
        if self.mean_height > 1.3:
            return True
        return False

    def compare_species(self, other: "TreeStratum") -> bool:
        if self.species is None or other.species is None:
            return False
        if self.species == other.species:
            return True
        return False

    def to_sapling_reference_tree(self) -> "ReferenceTree":
        result = ReferenceTree()
        result.stems_per_ha = self.sapling_stems_per_ha
        result.species = self.species
        result.breast_height_diameter = self.mean_diameter
        result.height = self.mean_height
        result.breast_height_age = self.breast_height_age
        result.biological_age = self.biological_age
        result.saw_log_volume_reduction_factor = -1.0
        result.pruning_year = 0
        result.age_when_10cm_diameter_at_breast_height = 0
        result.origin = self.origin
        result.stand_origin_relative_position = (0.0, 0.0, 0.0)
        result.management_category = 1
        result.sapling = True
        return result

    def get_breast_height_age(self, subtrahend: float = 12.0) -> float:
        if self.breast_height_age is not None and self.breast_height_age > 0.0:
            return self.breast_height_age
        if self.biological_age is not None and self.biological_age > 0.0:
            new_breast_height_age = self.biological_age - subtrahend
            return 0.0 if new_breast_height_age <= 0.0 else new_breast_height_age
        return 0.0

    def as_internal_csv_row(self) -> list[str]:
        return [
            "stratum",
            str(self.identifier),
            str(self.species),
            str(self.origin),
            str(self.stems_per_ha),
            str(self.mean_diameter),
            str(self.mean_height),
            str(self.breast_height_age),
            str(self.biological_age),
            str(self.basal_area),
            str(self.saw_log_volume_reduction_factor),
            str(self.cutting_year),
            str(self.age_when_10cm_diameter_at_breast_height),
            str(self.tree_number),
            str(self.stand_origin_relative_position[0]),
            str(self.stand_origin_relative_position[1]),
            str(self.stand_origin_relative_position[2]),
            str(self.lowest_living_branch_height),
            str(self.management_category),
            str(self.sapling_stems_per_ha),
            str(self.sapling_stratum),
            str(self.storey)
        ]

    @classmethod
    def from_csv_row(cls, row) -> "TreeStratum":
        result = cls()
        result.identifier = conv(row[1], str)
        result.species = TreeSpecies(int(row[2]))
        result.origin = conv(row[3], int)
        result.stems_per_ha = conv(row[4], float)
        result.mean_diameter = conv(row[5], float)
        result.mean_height = conv(row[6], float)
        result.breast_height_age = conv(row[7], float)
        result.biological_age = conv(row[8], float)
        result.basal_area = conv(row[9], float)
        result.saw_log_volume_reduction_factor = conv(row[10], float)
        result.cutting_year = conv(row[11], int)
        result.age_when_10cm_diameter_at_breast_height = conv(row[12], int)
        result.tree_number = conv(row[13], int)
        result.stand_origin_relative_position = (
            conv(row[14], float) or 0.0,
            conv(row[15], float) or 0.0,
            conv(row[16], float) or 0.0
        )
        result.lowest_living_branch_height = conv(row[17], float)
        result.management_category = conv(row[18], int)
        result.sapling_stems_per_ha = conv(row[19], float)
        result.sapling_stratum = row[20] == "True"
        result.storey = Storey(int(row[21])) if row[21] != "None" else None
        return result


@dataclass(init=True, repr=False, order=False, unsafe_hash=False, frozen=False, match_args=False, kw_only=False,
           slots=False, weakref_slot=False, eq=False)
class ReferenceTree():
    # VMI data type 3
    # No SMK equivalent

    stand: Optional["ForestStand"] = None

    # identifier of the tree within the container stand
    identifier: Optional[str] = None

    stems_per_ha: Optional[float] = None
    species: Optional[TreeSpecies] = None
    # diameter at 1.3 m height
    breast_height_diameter: Optional[float] = None
    height: Optional[float] = None  # model height in meters
    measured_height: Optional[float] = None  # measurement tree height
    # age in years when reached 1.3 m height
    breast_height_age: Optional[float] = None
    biological_age: Optional[float] = None  # age in years
    saw_log_volume_reduction_factor: Optional[float] = None  # value between 0.0-1.0
    pruning_year: int = 0
    # age when reached 10 cm diameter at 1.3 m height. Hard variable to name...
    age_when_10cm_diameter_at_breast_height: Optional[int] = None
    # 0-3; natural, seeded, planted, supplementary planted
    origin: Optional[int] = None
    # default is the order of appearance (or in sample plot)
    tree_number: Optional[int] = None
    # Angle from plot origin, distance (m) to plot origin, height difference (m) with plot origin
    stand_origin_relative_position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    lowest_living_branch_height: Optional[float] = None  # meters
    management_category: Optional[int] = None

    # VMI tree_category for living/dead/otherwise unusable tree
    tree_category: Optional[str] = None
    sapling: bool = False
    storey: Optional[Storey] = None
    tree_type: Optional[str] = None

    # VMI tuhon ilmiasu
    tuhon_ilmiasu: Optional[str] = None

    def __eq__(self, other):
        return id(self) == id(other)

    def __deepcopy__(self, memo: dict) -> 'ReferenceTree':
        t = ReferenceTree.__new__(ReferenceTree)
        t.__dict__.update(self.__dict__)
        return t

    def __hash__(self):
        return id(self)

    def validate(self):
        pass

    def has_biological_age(self) -> bool:
        if self.biological_age is None:
            return False
        if self.biological_age > 0.0:
            return True
        return False

    def has_diameter(self) -> bool:
        if self.breast_height_diameter is None:
            return False
        if self.breast_height_diameter > 0.0:
            return True
        return False

    def has_height_over_130_cm(self) -> bool:
        if self.height is None:
            return False
        if self.height > 1.3:
            return True
        return False

    def is_living(self) -> bool:
        return self.tree_category in (None, "0", "1", "3", "7")

    def compare_species(self, other: "ReferenceTree") -> bool:
        if self.species is None or other.species is None:
            return False
        if self.species == other.species:
            return True
        return False

    @classmethod
    def from_csv_row(cls, row) -> "ReferenceTree":
        result = cls()
        result.identifier = conv(row[1], str)
        result.species = TreeSpecies(int(row[2]))
        result.origin = conv(row[3], int)
        result.stems_per_ha = conv(row[4], float)
        result.breast_height_diameter = conv(row[5], float)
        result.height = conv(row[6], float)
        result.measured_height = conv(row[7], float)
        result.breast_height_age = conv(row[8], float)
        result.biological_age = conv(row[9], float)
        result.saw_log_volume_reduction_factor = conv(row[10], float)
        result.pruning_year = conv(row[11], int) or 0
        result.age_when_10cm_diameter_at_breast_height = conv(row[12], int)
        result.tree_number = conv(row[13], int)
        result.stand_origin_relative_position = (
            conv(row[14], float) or 0.0,
            conv(row[15], float) or 0.0,
            conv(row[16], float) or 0.0,
        )
        result.lowest_living_branch_height = conv(row[17], float)
        result.management_category = conv(row[18], int)
        result.tree_category = conv(row[19], str)
        result.sapling = row[20] == "True"
        result.storey = Storey(int(row[21])) if row[21] != 'None' else None
        result.tree_type = conv(row[22], str)
        result.tuhon_ilmiasu = conv(row[23], str)
        return result


@dataclass(init=True, repr=False, order=False, unsafe_hash=False, frozen=False, match_args=False, kw_only=False,
           slots=False, weakref_slot=False, eq=False)
class ForestStand(Finalizable):
    # VMI data type 1
    # SMK data type Stand

    reference_trees_pre_vec: list[ReferenceTree] = dataclasses.field(default_factory=list)
    tree_strata_pre_vec: list[TreeStratum] = dataclasses.field(default_factory=list)

    reference_trees: ReferenceTrees = ReferenceTrees()
    tree_strata: TreeStrata = TreeStrata()

    # unique identifier for entity within its domain
    identifier: str = ""

    management_unit_id: Optional[int] = None
    # default to management unit id unless overriden
    stand_id: Optional[int] = management_unit_id

    year: Optional[int] = None
    area: float = 0.0
    # default to area_ha, unless overridden
    area_weight: float = area

    # lat, lon, height above sea level (m), CRS
    geo_location: Optional[tuple[Optional[float], Optional[float], Optional[float], Optional[str]]] = None

    degree_days: Optional[float] = None
    owner_category: Optional[OwnerCategory] = None
    land_use_category: Optional[LandUseCategory] = None
    soil_peatland_category: Optional[SoilPeatlandCategory] = None
    site_type_category: Optional[SiteType] = None
    tax_class_reduction: Optional[int] = None
    tax_class: Optional[int] = None
    drainage_category: Optional[DrainageCategory] = None
    drainage_feasibility: Optional[bool] = None
    drainage_year: Optional[int] = None
    fertilization_year: Optional[int] = None
    soil_surface_preparation_year: Optional[int] = None
    natural_regeneration_feasibility: Optional[bool] = None
    regeneration_area_cleaning_year: Optional[int] = None
    development_class: Optional[int] = None
    artificial_regeneration_year: Optional[int] = None
    young_stand_tending_year: Optional[int] = None
    pruning_year: Optional[int] = None
    cutting_year: Optional[int] = None
    forestry_centre_id: Optional[int] = None
    forest_management_category: Optional[int | float] = None
    method_of_last_cutting: Optional[int] = None
    municipality_id: Optional[int] = None
    dominant_storey_age: Optional[float] = None

    # stand specific factors for scaling estimated ReferenceTree count per hectare
    area_weight_factors: tuple[float, float] = (1.0, 1.0)

    fra_category: Optional[str] = None  # VMI fra category
    # VMI land use category detail
    land_use_category_detail: Optional[str] = None
    # VMI stand number > 1 (meaning sivukoeala, auxiliary stand)
    auxiliary_stand: bool = False

    monthly_temperatures: Optional[list[float]] = None
    monthly_rainfall: Optional[list[float]] = None
    sea_effect: Optional[float] = None
    lake_effect: Optional[float] = None

    basal_area: Optional[float] = None

    def __eq__(self, other):
        return id(self) == id(other)

    def __deepcopy__(self, memo: dict) -> 'ForestStand':
        stand = ForestStand.__new__(ForestStand)
        stand.__dict__.update(self.__dict__)
        if self.reference_trees_soa is None or self.tree_strata_soa is None:
            stand.reference_trees = [t.__deepcopy__(memo) for t in stand.reference_trees]
            stand.tree_strata = [s.__deepcopy__(memo) for s in stand.tree_strata]
        else:
            stand.reference_trees_soa = self.reference_trees_soa.finalize()
            stand.tree_strata_soa = self.tree_strata_soa.finalize()
        if self.monthly_temperatures is not None:
            stand.monthly_temperatures = list(self.monthly_temperatures)
        if self.monthly_rainfall is not None:
            stand.monthly_rainfall = list(self.monthly_rainfall)
        return stand

    def __hash__(self):
        return id(self)

    def set_identifiers(self, stand_id: Optional[int], management_unit_id: Optional[int] = None):
        self.stand_id = stand_id
        self.management_unit_id = (
            stand_id if management_unit_id is None else management_unit_id
        )

    def set_area(self, area_ha: float | None):
        if area_ha is None:
            raise MetsiException("Area missing")
        if self.is_auxiliary():
            self.area = 0.0
        else:
            self.area = area_ha
        self.area_weight = area_ha

    def set_geo_location(self, lat: Optional[float], lon: Optional[float],
                         height: Optional[float], system: str = "EPSG:3067"):
        if not lat or not lon:
            raise ValueError("Invalid source values for geo location")
        self.geo_location = (lat, lon, height, system)

    def validate(self):
        pass

    def add_tree(self, tree: ReferenceTree):
        self.reference_trees.append(tree)

    def is_auxiliary(self):
        return self.auxiliary_stand

    def is_forest_land(self):
        return (self.land_use_category.value < 4) if self.land_use_category is not None else False

    def is_other_excluded_forest(self):
        return (
            self.land_use_category == MelaLandUseCategory.OTHER
            and self.fra_category == "3"
            and self.land_use_category_detail in ("1", "2", "6", "7")
        )

    def has_trees(self):
        return len(self.reference_trees) > 0

    def has_strata(self):
        return len(self.tree_strata) > 0

    def from_row(self, row):
        self.management_unit_id = conv(row[0], int)
        self.year = conv(row[1], int)
        self.area = conv(row[2], float) or 0.0
        self.area_weight = conv(row[3], float) or 0.0
        self.geo_location = (
            conv(row[4], float),
            conv(row[5], float),
            conv(row[6], float),
            conv(row[7], str)
        )
        self.degree_days = conv(row[8], float)
        self.owner_category = conv(row[9], OwnerCategory)
        self.land_use_category = conv(row[10], LandUseCategory)
        self.soil_peatland_category = conv(row[11], SoilPeatlandCategory)
        self.site_type_category = conv(row[12], SiteType)
        self.tax_class_reduction = conv(row[13], int)
        self.tax_class = conv(row[14], int)
        self.drainage_category = conv(row[15], DrainageCategory)
        self.drainage_feasibility = (row[16] == "True") if row[16] != "None" else None
        self.drainage_year = conv(row[17], int)
        self.fertilization_year = conv(row[18], int)
        self.soil_surface_preparation_year = conv(row[19], int)
        self.natural_regeneration_feasibility = (row[20] == "True") if row[20] != "None" else None
        self.regeneration_area_cleaning_year = conv(row[21], int)
        self.development_class = conv(row[22], int)
        self.artificial_regeneration_year = conv(row[23], int)
        self.young_stand_tending_year = conv(row[24], int)
        self.pruning_year = conv(row[25], int)
        self.cutting_year = conv(row[26], int)
        self.forestry_centre_id = conv(row[27], int)
        self.forest_management_category = conv(row[28], int)
        self.method_of_last_cutting = conv(row[29], int)
        self.municipality_id = conv(row[30], int)
        self.fra_category = conv(row[31], str)
        self.land_use_category_detail = conv(row[32], str)
        self.auxiliary_stand = row[33] == "True"
        self.area_weight_factors = (conv(row[34], float) or 0.0, conv(row[35], float) or 0.0)
        self.stand_id = conv(row[36], int)
        self.basal_area = conv(row[37], float)
        self.dominant_storey_age = conv(row[38], float)

    @classmethod
    def from_csv_row(cls, row) -> "ForestStand":
        stand = cls()
        stand.identifier = row[1]
        stand.from_row(row[2:])
        return stand

    def get_value_list(self, keys: Optional[list[str]] = None) -> list:
        """ Returns instance values as list based on keys.
            If keys are not present all attribute values are returned """
        ad = []
        if keys is not None:
            ad = [getattr(self, k) for k in keys]  # Needs to fail noisy
        return ad

    @override
    def finalize(self):
        if self.reference_trees_soa is not None and self.tree_strata_soa is not None:
            self.reference_trees_soa = self.reference_trees_soa.finalize()
            self.tree_strata_soa = self.tree_strata_soa.finalize()


def create_layered_tree(**kwargs) -> LayeredObject[ReferenceTree]:
    prototype = ReferenceTree()
    layered = LayeredObject(prototype)
    for k, v in kwargs.items():
        setattr(layered, k, v)
    return layered


def create_layered_stand(**kwargs) -> LayeredObject[ForestStand]:
    prototype = ForestStand()
    layered = LayeredObject(prototype)
    for k, v in kwargs.items():
        setattr(layered, k, v)
    return layered


def create_layered_stratum(**kwargs) -> LayeredObject[TreeStratum]:
    prototype = TreeStratum()
    layered = LayeredObject(prototype)
    for k, v in kwargs.items():
        setattr(layered, k, v)
    return layered


def stand_as_internal_csv_row(stand: PossiblyLayered[ForestStand], decl_keys: Optional[list[str]] = None) -> list[str]:
    result = ["stand", stand.identifier]
    result.extend(stand_as_internal_row(stand))
    if decl_keys is not None:
        result.extend(stand.get_value_list(decl_keys))
    return result


def tree_as_internal_csv_row(tree: PossiblyLayered[ReferenceTree]) -> list[str]:
    return [
        "tree",
        str(tree.identifier),
        str(tree.species),
        str(tree.origin),
        str(tree.stems_per_ha),
        str(tree.breast_height_diameter),
        str(tree.height),
        str(tree.measured_height),
        str(tree.breast_height_age),
        str(tree.biological_age),
        str(tree.saw_log_volume_reduction_factor),
        str(tree.pruning_year),
        str(tree.age_when_10cm_diameter_at_breast_height),
        str(tree.tree_number),
        str(tree.stand_origin_relative_position[0]),
        str(tree.stand_origin_relative_position[1]),
        str(tree.stand_origin_relative_position[2]),
        str(tree.lowest_living_branch_height),
        str(tree.management_category),
        str(tree.tree_category),
        str(tree.sapling),
        str(tree.storey),
        str(tree.tree_type),
        str(tree.tuhon_ilmiasu)
    ]


def stratum_as_internal_csv_row(stratum: PossiblyLayered[TreeStratum]) -> list[str]:
    return [
        "stratum",
        str(stratum.identifier),
        str(stratum.species),
        str(stratum.origin),
        str(stratum.stems_per_ha),
        str(stratum.mean_diameter),
        str(stratum.mean_height),
        str(stratum.breast_height_age),
        str(stratum.biological_age),
        str(stratum.basal_area),
        str(stratum.saw_log_volume_reduction_factor),
        str(stratum.cutting_year),
        str(stratum.age_when_10cm_diameter_at_breast_height),
        str(stratum.tree_number),
        str(stratum.stand_origin_relative_position[0]),
        str(stratum.stand_origin_relative_position[1]),
        str(stratum.stand_origin_relative_position[2]),
        str(stratum.lowest_living_branch_height),
        str(stratum.management_category),
        str(stratum.sapling_stems_per_ha),
        str(stratum.sapling_stratum),
        str(stratum.storey)
    ]


def stand_as_rst_row(stand: PossiblyLayered[ForestStand]):
    return [
        stand.management_unit_id,
        stand.year,
        stand.area,
        stand.area_weight,
        stand.geo_location[0] if stand.geo_location else None,
        stand.geo_location[1] if stand.geo_location else None,
        stand.stand_id,
        stand.geo_location[2] if stand.geo_location else None,
        stand.degree_days,
        stand.owner_category.value if stand.owner_category else None,
        stand.land_use_category.value if stand.land_use_category else None,
        stand.soil_peatland_category,
        stand.site_type_category,
        stand.tax_class_reduction,
        stand.tax_class,
        stand.drainage_category,
        stand.drainage_feasibility,
        None,
        stand.drainage_year,
        stand.fertilization_year,
        stand.soil_surface_preparation_year,
        stand.natural_regeneration_feasibility,
        stand.regeneration_area_cleaning_year,
        stand.development_class,
        stand.artificial_regeneration_year,
        stand.young_stand_tending_year,
        stand.pruning_year,
        stand.cutting_year,
        stand.forestry_centre_id,
        stand.forest_management_category,
        stand.method_of_last_cutting,
        stand.municipality_id,
        None,
        stand.dominant_storey_age,
    ]


def stand_as_internal_row(stand: PossiblyLayered[ForestStand]):
    return [
        stand.management_unit_id,
        stand.year,
        stand.area,
        stand.area_weight,
        stand.geo_location[0] if stand.geo_location is not None else None,
        stand.geo_location[1] if stand.geo_location is not None else None,
        stand.geo_location[2] if stand.geo_location is not None else None,
        stand.geo_location[3] if stand.geo_location is not None else None,
        stand.degree_days,
        stand.owner_category,
        stand.land_use_category,
        stand.soil_peatland_category,
        stand.site_type_category,
        stand.tax_class_reduction,
        stand.tax_class,
        stand.drainage_category,
        stand.drainage_feasibility,
        stand.drainage_year,
        stand.fertilization_year,
        stand.soil_surface_preparation_year,
        stand.natural_regeneration_feasibility,
        stand.regeneration_area_cleaning_year,
        stand.development_class,
        stand.artificial_regeneration_year,
        stand.young_stand_tending_year,
        stand.pruning_year,
        stand.cutting_year,
        stand.forestry_centre_id,
        stand.forest_management_category,
        stand.method_of_last_cutting,
        stand.municipality_id,
        stand.fra_category,
        stand.land_use_category_detail,
        stand.auxiliary_stand,
        stand.area_weight_factors[0],
        stand.area_weight_factors[1],
        stand.stand_id,
        stand.basal_area,
        stand.dominant_storey_age
    ]


def tree_as_rst_row(tree: PossiblyLayered[ReferenceTree]):
    return [
        tree.stems_per_ha,
        tree.species,
        tree.breast_height_diameter,
        tree.height,
        tree.breast_height_age,
        tree.biological_age,
        tree.saw_log_volume_reduction_factor,
        tree.pruning_year,
        tree.age_when_10cm_diameter_at_breast_height,
        tree.origin,
        tree.tree_number,
        tree.stand_origin_relative_position[0],
        tree.stand_origin_relative_position[1],
        tree.stand_origin_relative_position[2],
        tree.lowest_living_branch_height,
        tree.management_category,
        None,
    ]


def stratum_as_rsts_row(stratum: PossiblyLayered[TreeStratum]):
    return [
        stratum.tree_number,
        stratum.species,
        stratum.origin,
        stratum.stems_per_ha,
        stratum.mean_diameter,
        stratum.mean_height,
        stratum.breast_height_age,
        stratum.biological_age,
        stratum.basal_area,
        stratum.sapling_stems_per_ha,
        stratum.storey,
        stratum.number_of_generated_trees
    ]
