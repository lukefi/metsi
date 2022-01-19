import typing

class ReferenceTree:


    def __init__(self, **d):
        self.stand: ForestStand or None = None

        # identifier of the tree within the container stand
        self.identifier: str or None = None

        self.stems_per_ha: float or None = None
        self.species: int or None = None
        self.diameter_at_130_cm: float or None = None
        self.height_m: float or None = None
        self.d13_age: float or None = None
        self.biological_age: float or None = None
        self.saw_log_volume_reduction_factor: float or None = None
        self.pruning_year: int = 0
        self.age_d10_at_h130: int = 0
        self.origin: int or None = None
        self.tree_id: int or None = None
        self.angle_from_plot_origin_deg: float or None = None
        self.distance_from_plot_origin_m: float or None = None
        self.height_difference_to_plot_origin_m: float or None = None
        self.height_of_lowest_living_branch_m: float or None = None
        self.management_category: int or None = None

        for key, value in d.items():
            self.__setattr__(key, value)



    def __eq__(self, other):
        return self.identifier == other.identifier

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
        if self.diameter_at_130_cm is None:
            return False
        elif self.diameter_at_130_cm > 0.0:
            return True
        else:
            return False

    def has_heigth_over_130_cm(self) -> bool:
        if self.height_m is None:
            return False
        elif self.height_m > 1.3:
            return True
        else:
            return False

    def compare_species(self, record) -> bool:
        if self.species is None or record.species is None:
            return False
        elif self.species == record.species:
            return True
        else:
            return False


class ForestStand:


    def __init__(self, **d):
        self.reference_trees: typing.List[ReferenceTree] = []
        self.tree_strata: typing.List[TreeStratum] = []

        self.identifier: str or None = None  # unique identifier for entity within its domain

        self.management_unit_id: int or None = None
        self.stand_id: int or None = self.management_unit_id

        self.year: int or None = None
        self.area_ha: float = 0.0
        self.area_weight: float = self.area_ha


        # lat, lon, height above sea level (m), CRS
        self.geo_location: typing.Tuple[float, float, float, str] or None = None

        self.degree_days: float or None = None
        self.owner_category: int or None = None
        self.land_use_category: int or None = None
        self.soil_peatland_category: int or None = None
        self.site_type_category: int or None = None
        self.tax_class_reduction: int or None = None
        self.tax_class: int or None = None
        self.drainage_category: int or None = None
        self.drainage_feasibility: bool or None = None

        self.drainage_year: int or None = None
        self.fertilization_year: int or None = None
        self.soil_preparation_year: int or None = None
        self.natural_regen_feasibility: bool or None = None
        self.regen_area_cleaning_year: int or None = None
        self.development_class: int or None = None
        self.artificial_regen_year: int or None = None
        self.young_stand_tending_year: int or None = None
        self.pruning_year: int or None = None
        self.cutting_year: int or None = None
        self.forestry_centre_id: int or None = None
        self.forest_management_category: int or None = None
        self.method_of_last_cutting: int or None = None
        self.municipality_id: int or None = None

        for key, value in d.items():
            self.__setattr__(key, value)


        # stand specific factors for scaling estimated ReferenceTree count per hectare
        self.reference_tree_scaling_factors: typing.Tuple[float, float] = (1.0, 1.0)

    def __eq__(self, other):
        return self.identifier == other.identifier

    def set_identifiers(self, stand_id: int, management_unit_id: int or None = None):
        self.stand_id = stand_id
        self.management_unit_id = stand_id if management_unit_id is None else management_unit_id

    def set_area(self, area_ha: float, area_weight: float or None = None):
        self.area_ha = area_ha
        self.area_weight = area_ha if area_weight is None else area_weight

    def set_geo_location(self, lat: float, lon: float, height: float, system: str = "ERTS-TM35FIN"):
        if not lat or not lon:
            raise ValueError("Invalid source values for geo location")
        self.geo_location = (lat, lon, height, system)

    def validate(self):
        pass

    def add_tree(self, tree: ReferenceTree):
        self.reference_trees.append(tree)
