import dataclasses
from typing import Optional
from dataclasses import dataclass
from lukefi.metsi.data.conversion.internal2mela import mela_stand, mela_tree, mela_stratum
from lukefi.metsi.data.enums.internal import LandUseCategory, OwnerCategory, SiteType, SoilPeatlandCategory, \
    TreeSpecies, DrainageCategory, Storey
from lukefi.metsi.data.enums.mela import MelaLandUseCategory
from lukefi.metsi.data.formats.util import convert_str_to_type, get_or_default
from lukefi.metsi.data.layered_model import LayeredObject


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

@dataclass
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

    def __eq__(self, other: "TreeStratum"):
        return id(self) == id(other)

    def __deepcopy__(self, memo: dict) -> 'TreeStratum':
        s = TreeStratum.__new__(TreeStratum)
        s.__dict__.update(self.__dict__)
        return s

    def has_height(self):
        if self.mean_height is None:
            return False
        elif self.mean_height > 0.0:
            return True
        else:
            return False

    def has_sapling_stems_per_ha(self) -> bool:
        if self.sapling_stems_per_ha is None:
            return False
        elif self.sapling_stems_per_ha > 0.0:
            return True
        else:
            return False

    def has_stems_per_ha(self) -> bool:
        if self.stems_per_ha is None:
            return False
        elif self.stems_per_ha > 0.0:
            return True
        else:
            return False

    def has_diameter(self) -> bool:
        if self.mean_diameter is None:
            return False
        elif self.mean_diameter > 0.0:
            return True
        else:
            return False

    def has_breast_height_age(self) -> bool:
        if self.breast_height_age is None:
            return False
        elif self.breast_height_age > 0.0:
            return True
        else:
            return False

    def has_biological_age(self) -> bool:
        if self.biological_age is None:
            return False
        elif self.biological_age > 0.0:
            return True
        else:
            return False

    def has_basal_area(self) -> bool:
        if self.basal_area is None:
            return False
        elif self.basal_area > 0.0:
            return True
        else:
            return False

    def has_height_over_130_cm(self) -> bool:
        if self.mean_height is None:
            return False
        elif self.mean_height > 1.3:
            return True
        else:
            return False

    def compare_species(self, other: "TreeStratum") -> bool:
        if self.species is None or other.species is None:
            return False
        elif self.species == other.species:
            return True
        else:
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
        if self.has_breast_height_age():
            return self.breast_height_age
        elif self.has_biological_age():
            new_breast_height_age = self.biological_age - subtrahend
            return 0.0 if new_breast_height_age <= 0.0 else new_breast_height_age
        else:
            return 0.0

    def as_internal_csv_row(self) -> list[str]:
        return [
            "stratum",
            self.identifier,
            self.species,
            self.origin,
            self.stems_per_ha,
            self.mean_diameter,
            self.mean_height,
            self.breast_height_age,
            self.biological_age,
            self.basal_area,
            self.saw_log_volume_reduction_factor,
            self.cutting_year,
            self.age_when_10cm_diameter_at_breast_height,
            self.tree_number,
            self.stand_origin_relative_position[0],
            self.stand_origin_relative_position[1],
            self.stand_origin_relative_position[2],
            self.lowest_living_branch_height,
            self.management_category,
            self.sapling_stems_per_ha,
            self.sapling_stratum,
            self.storey
        ]

    @classmethod
    def from_csv_row(cls, row) -> "TreeStratum":
        def conv(value, property_name):
            return convert_str_to_type(cls, value, property_name)

        result = cls()
        result.identifier = conv(row[1], "identifier")
        result.species = TreeSpecies(int(row[2]))
        result.origin = conv(row[3], "origin")
        result.stems_per_ha = conv(row[4], "stems_per_ha")
        result.mean_diameter = conv(row[5], "mean_diameter")
        result.mean_height = conv(row[6], "mean_height")
        result.breast_height_age = conv(row[7], "breast_height_age")
        result.biological_age = conv(row[8], "biological_age")
        result.basal_area = conv(row[9], "basal_area")
        result.saw_log_volume_reduction_factor = conv(row[10], "saw_log_volume_reduction_factor")
        result.cutting_year = conv(row[11], "cutting_year")
        result.age_when_10cm_diameter_at_breast_height = conv(row[12], "age_when_10cm_diameter_at_breast_height")
        result.tree_number = conv(row[13], "tree_number")
        result.stand_origin_relative_position = conv((row[14],row[15],row[16]),  "stand_origin_relative_position")
        result.lowest_living_branch_height = conv(row[17], "lowest_living_branch_height")
        result.management_category = conv(row[18], "management_category")
        result.sapling_stems_per_ha = conv(row[19], "sapling_stems_per_ha")
        result.sapling_stratum = conv(row[20], "sapling_stratum")
        result.storey = Storey(int(row[21])) if row[21] != "None" else None
        return result
    
    def as_rsts_row(self):
        melaed = mela_stratum(self)
        rsts_result = [
            melaed.tree_number,
            0 if melaed.species is None else melaed.species.value,
            melaed.origin,
            melaed.stems_per_ha,
            melaed.mean_diameter,
            melaed.mean_height,
            melaed.breast_height_age,
            melaed.biological_age,
            melaed.basal_area,
            melaed.sapling_stems_per_ha,
            0 if melaed.storey is None else melaed.storey.value,
            melaed.number_of_generated_trees
        ]
        return [ get_or_default(v, -1) for v in rsts_result ]

@dataclass
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
    saw_log_volume_reduction_factor: Optional[float] = None # value between 0.0-1.0
    pruning_year: int = 0
    # age when reached 10 cm diameter at 1.3 m height. Hard variable to name...
    age_when_10cm_diameter_at_breast_height: int = None
    # 0-3; natural, seeded, planted, supplementary planted
    origin: Optional[int] = None
    # default is the order of appearance (or in sample plot)
    tree_number: Optional[int] = None
    # Angle from plot origin, distance (m) to plot origin, height difference (m) with plot origin
    stand_origin_relative_position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    lowest_living_branch_height: Optional[float] = None # meters
    management_category: Optional[int] = None

    # VMI tree_category for living/dead/otherwise unusable tree
    tree_category: Optional[str] = None
    sapling: bool = False
    storey: Optional[Storey] = None
    tree_type: Optional[str] = None

    # VMI tuhon ilmiasu
    tuhon_ilmiasu: Optional[str] = None
    
    def __eq__(self, other: "ReferenceTree"):
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
        elif self.biological_age > 0.0:
            return True
        else:
            return False

    def has_diameter(self) -> bool:
        if self.breast_height_diameter is None:
            return False
        elif self.breast_height_diameter > 0.0:
            return True
        else:
            return False

    def has_height_over_130_cm(self) -> bool:
        if self.height is None:
            return False
        elif self.height > 1.3:
            return True
        else:
            return False

    def is_living(self) -> bool:
        return self.tree_category in (None, "0", "1", "3", "7")

    def compare_species(self, other: "ReferenceTree") -> bool:
        if self.species is None or other.species is None:
            return False
        elif self.species == other.species:
            return True
        else:
            return False

    def as_internal_csv_row(self) -> list[str]:
        return [
            "tree",
            self.identifier,
            self.species,
            self.origin,
            self.stems_per_ha,
            self.breast_height_diameter,
            self.height,
            self.measured_height,
            self.breast_height_age,
            self.biological_age,
            self.saw_log_volume_reduction_factor,
            self.pruning_year,
            self.age_when_10cm_diameter_at_breast_height,
            self.tree_number,
            self.stand_origin_relative_position[0],
            self.stand_origin_relative_position[1],
            self.stand_origin_relative_position[2],
            self.lowest_living_branch_height,
            self.management_category,
            self.tree_category,
            self.sapling,
            self.storey,
            self.tree_type,
            self.tuhon_ilmiasu
        ]

    @classmethod
    def from_csv_row(cls, row) -> "ReferenceTree":
        def conv(value, property_name):
            return convert_str_to_type(cls, value, property_name)
        result = cls()
        result.identifier = conv(row[1], "identifier")
        result.species = TreeSpecies(int(row[2]))
        result.origin = conv(row[3], "origin")
        result.stems_per_ha = conv(row[4], "stems_per_ha")
        result.breast_height_diameter = conv(row[5], "breast_height_diameter")
        result.height = conv(row[6], "height")
        result.measured_height = conv(row[7], "measured_height")
        result.breast_height_age = conv(row[8], "breast_height_age")
        result.biological_age = conv(row[9], "biological_age")
        result.saw_log_volume_reduction_factor = conv(row[10], "saw_log_volume_reduction_factor")
        result.pruning_year = conv(row[11], "pruning_year")
        result.age_when_10cm_diameter_at_breast_height = conv(row[12], "age_when_10cm_diameter_at_breast_height")
        result.tree_number = conv(row[13], "tree_number")
        result.stand_origin_relative_position = conv((
            row[14],
            row[15],
            row[16],
        ), "stand_origin_relative_position")
        result.lowest_living_branch_height = conv(row[17], "lowest_living_branch_height")
        result.management_category = conv(row[18], "management_category")
        result.tree_category = conv(row[19], "tree_category")
        result.sapling = conv(row[20], "sapling")
        result.storey = Storey(int(row[21])) if row[21] != 'None' else None
        result.tree_type = conv(row[22], "tree_type")
        result.tuhon_ilmiasu = conv(row[23], "tuhon_ilmiasu")
        return result


    def as_rst_row(self):
        melaed = mela_tree(self)
        saw_log_volume_reduction_factor = (
            -1
            if melaed.saw_log_volume_reduction_factor is None
            else melaed.saw_log_volume_reduction_factor
        )
        return [
            melaed.stems_per_ha,
            0 if melaed.species is None else melaed.species.value,
            melaed.breast_height_diameter,
            melaed.height,
            melaed.breast_height_age,
            melaed.biological_age,
            saw_log_volume_reduction_factor,
            melaed.pruning_year,
            melaed.age_when_10cm_diameter_at_breast_height,
            melaed.origin,
            melaed.tree_number,
            melaed.stand_origin_relative_position[0],
            melaed.stand_origin_relative_position[1],
            melaed.stand_origin_relative_position[2],
            melaed.lowest_living_branch_height,
            melaed.management_category,
            None,
        ]


@dataclass
class ForestStand():
    # VMI data type 1
    # SMK data type Stand

    reference_trees: list[ReferenceTree] = dataclasses.field(default_factory=list)
    tree_strata: list[TreeStratum] = dataclasses.field(default_factory=list)

    # unique identifier for entity within its domain
    identifier: Optional[str] = None

    management_unit_id: Optional[int] = None
    # default to management unit id unless overriden
    stand_id: Optional[int] = management_unit_id

    year: Optional[int] = None
    area: float = 0.0
    # default to area_ha, unless overridden
    area_weight: float = area

    # lat, lon, height above sea level (m), CRS
    geo_location: Optional[tuple[float, float, float, str]] = None

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
    forest_management_category: Optional[int] = None
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

    def __eq__(self, other: "ForestStand"):
        return id(self) == id(other)

    def __deepcopy__(self, memo: dict) -> 'ForestStand':
        stand = ForestStand.__new__(ForestStand)
        stand.__dict__.update(self.__dict__)
        stand.reference_trees = [t.__deepcopy__(memo) for t in stand.reference_trees]
        stand.tree_strata = [s.__deepcopy__(memo) for s in stand.tree_strata]
        if stand.monthly_temperatures is not None:
            stand.monthly_temperatures = list(stand.monthly_temperatures)
        if stand.monthly_rainfall is not None:
            stand.monthly_rainfall = list(stand.monthly_rainfall)
        return stand

    def __hash__(self):
        return id(self)

    def set_identifiers(self, stand_id: int, management_unit_id: Optional[int] = None):
        self.stand_id = stand_id
        self.management_unit_id = (
            stand_id if management_unit_id is None else management_unit_id
        )

    def set_area(self, area_ha: float):
        if self.is_auxiliary():
            self.area = 0.0
        else:
            self.area = area_ha
        self.area_weight = area_ha

    def set_geo_location(
        self, lat: float, lon: float, height: float, system: str = "EPSG:3067"
    ):
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
        return self.land_use_category.value < 4

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

    def as_internal_csv_row(self) -> list[str]:
        result = ["stand", self.identifier]
        result.extend(self.as_internal_row())
        return result

    def as_internal_row(self):
        return [
            self.management_unit_id,
            self.year,
            self.area,
            self.area_weight,
            self.geo_location[0],
            self.geo_location[1],
            self.geo_location[2],
            self.geo_location[3],
            self.degree_days,
            self.owner_category,
            self.land_use_category,
            self.soil_peatland_category,
            self.site_type_category,
            self.tax_class_reduction,
            self.tax_class,
            self.drainage_category,
            self.drainage_feasibility,
            self.drainage_year,
            self.fertilization_year,
            self.soil_surface_preparation_year,
            self.natural_regeneration_feasibility,
            self.regeneration_area_cleaning_year,
            self.development_class,
            self.artificial_regeneration_year,
            self.young_stand_tending_year,
            self.pruning_year,
            self.cutting_year,
            self.forestry_centre_id,
            self.forest_management_category,
            self.method_of_last_cutting,
            self.municipality_id,
            self.fra_category,
            self.land_use_category_detail,
            self.auxiliary_stand,
            self.area_weight_factors[0],
            self.area_weight_factors[1],
            self.stand_id,
            self.basal_area,
            self.dominant_storey_age
        ]

    def from_row(self, row):

        def conv(value, property_name):
            return convert_str_to_type(self, value, property_name)

        self.management_unit_id = conv(row[0], "management_unit_id")
        self.year = conv(row[1], "year")
        self.area = conv(row[2], "area")
        self.area_weight = conv(row[3], "area_weight")
        self.geo_location = conv((
            row[4],
            row[5],
            row[6],
            row[7],
        ), "geo_location")
        self.degree_days = conv(row[8], "degree_days")
        self.owner_category = conv(row[9], "owner_category")
        self.land_use_category = conv(row[10], "land_use_category")
        self.soil_peatland_category = conv(row[11], "soil_peatland_category")
        self.site_type_category = conv(row[12], "site_type_category")
        self.tax_class_reduction = conv(row[13], "tax_class_reduction")
        self.tax_class = conv(row[14], "tax_class")
        self.drainage_category = conv(row[15], "drainage_category")
        self.drainage_feasibility = conv(row[16], "drainage_feasibility")
        self.drainage_year = conv(row[17], "drainage_year")
        self.fertilization_year = conv(row[18], "fertilization_year")
        self.soil_surface_preparation_year = conv(row[19], "soil_surface_preparation_year")
        self.natural_regeneration_feasibility = conv(row[20], "natural_regeneration_feasibility")
        self.regeneration_area_cleaning_year = conv(row[21], "regeneration_area_cleaning_year")
        self.development_class = conv(row[22], "development_class")
        self.artificial_regeneration_year = conv(row[23], "artificial_regeneration_year")
        self.young_stand_tending_year = conv(row[24], "young_stand_tending_year")
        self.pruning_year = conv(row[25], "pruning_year")
        self.cutting_year = conv(row[26], "cutting_year")
        self.forestry_centre_id = conv(row[27], "forestry_centre_id")
        self.forest_management_category = conv(row[28], "forest_management_category")
        self.method_of_last_cutting = conv(row[29], "method_of_last_cutting")
        self.municipality_id = conv(row[30], "municipality_id")
        self.fra_category = conv(row[31], "fra_category")
        self.land_use_category_detail = conv(row[32], "land_use_category_detail")
        self.auxiliary_stand = conv(row[33], "auxiliary_stand")
        self.area_weight_factors = conv((row[34], row[35]), "area_weight_factors")
        self.stand_id = conv(row[36], "stand_id")
        self.basal_area = conv(row[37], "basal_area")
        self.dominant_storey_age = conv(row[38], "dominant_storey_age")


    @classmethod
    def from_csv_row(cls, row) -> "ForestStand":
        stand = cls()
        stand.identifier = row[1]
        stand.from_row(row[2:])
        return stand


    def as_rst_row(self):
        melaed = mela_stand(self)
        forestry_centre_id = (
            -1 if melaed.forestry_centre_id is None else melaed.forestry_centre_id
        )
        municipality_id = (
            -1 if melaed.municipality_id is None else melaed.municipality_id
        )
        return [
            melaed.management_unit_id,
            melaed.year,
            melaed.area,
            melaed.area_weight,
            melaed.geo_location[0],
            melaed.geo_location[1],
            melaed.stand_id,
            melaed.geo_location[2],
            melaed.degree_days,
            melaed.owner_category.value,
            melaed.land_use_category.value,
            0 if melaed.soil_peatland_category is None else melaed.soil_peatland_category.value,
            0 if melaed.site_type_category is None else melaed.site_type_category.value,
            melaed.tax_class_reduction,
            melaed.tax_class,
            0 if melaed.drainage_category is None else melaed.drainage_category.value,
            melaed.drainage_feasibility,
            None,
            melaed.drainage_year,
            melaed.fertilization_year,
            melaed.soil_surface_preparation_year,
            melaed.natural_regeneration_feasibility,
            melaed.regeneration_area_cleaning_year,
            melaed.development_class,
            melaed.artificial_regeneration_year,
            melaed.young_stand_tending_year,
            melaed.pruning_year,
            melaed.cutting_year,
            forestry_centre_id,
            melaed.forest_management_category,
            melaed.method_of_last_cutting,
            municipality_id,
            None,
            melaed.dominant_storey_age,
        ]


def create_layered_tree(**kwargs) -> LayeredObject[ReferenceTree]:
    prototype = ReferenceTree()
    layered = LayeredObject(prototype)
    for k, v in kwargs.items():
        layered.__setattr__(k, v)
    return layered


def create_layered_stand(**kwargs) -> LayeredObject[ForestStand]:
    prototype = ForestStand()
    layered = LayeredObject(prototype)
    for k, v in kwargs.items():
        layered.__setattr__(k, v)
    return layered


def create_layered_stratum(**kwargs) -> LayeredObject[TreeStratum]:
    prototype = TreeStratum()
    layered = LayeredObject(prototype)
    for k, v in kwargs.items():
        layered.__setattr__(k, v)
    return layered
