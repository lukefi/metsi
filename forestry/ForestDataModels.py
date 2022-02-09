import typing


class ReferenceTree:
    def __init__(self, **d):
        self.stand: ForestStand or None = None
        # identifier of the tree within the container stand
        self.identifier: str or None = None
        self.stems_per_ha: float or None = None  # RSD record 1
        self.species: int or None = None  # RSD record 2, 1-8
        self.breast_height_diameter: float or None = None  # RSD record 3, diameter at 1.3 m height
        self.height: float or None = None  # RSD record 4, height in meters
        self.breast_height_age: float or None = None  # RSD record 5, age in years when reached 1.3 m height
        self.biological_age: float or None = None  # RSD record 6, age in years
        self.saw_log_volume_reduction_factor: float or None = None  # RSD record 7, 0.0-1.0
        self.pruning_year: int = 0  # RSD record 8
        self.age_when_10cm_diameter_at_breast_height: int = 0  # RSD record 9, age when reached 10 cm diameter at 1.3 m height. Hard variable to name...
        self.origin: int or None = None  # RSD record 10, 0-3; natural, seeded, planted, supplementary planted
        self.tree_number: int or None = None  # RSD record 11, default is the order of appearance (or in sample plot)
        # RSD records 12, 13, 14.
        # Angle from plot origin, distance (m) to plot origin, height difference (m) with plot origin
        self.stand_origin_relative_position: typing.Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.lowest_living_branch_height: float or None = None  # RSD record 15, meters
        self.management_category: int or None = None  # RSD record 16
        # RSD record 17 reserved for system

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
        self.identifier: str or None = None  # unique identifier for entity within its domain
        self.management_unit_id: int or None = None  # RSD record 1
        self.stand_id: int or None = self.management_unit_id  # RSD record 7 (default to management unit id unless overriden)
        self.year: int or None = None  # RSD record 2
        self.area: float = 0.0  # RSD record 3
        self.area_weight: float = self.area  # RSD record 4 (default to area_ha, unless overridden)
        # RSD records 5 (lat), 6 (lon) in ERTS-TM35FIN (EPSG:3067), 8 (height)
        # lat, lon, height above sea level (m), CRS
        self.geo_location: typing.Tuple[float, float, float, str] or None = None
        self.degree_days: float or None = None  # RSD record 9
        self.owner_category: int or None = None  # RSD record 10, 0-4
        self.land_use_category: int or None = None  # RSD record 11, 1-9
        self.soil_peatland_category: int or None = None  # RSD record 12, 1-5
        self.site_type_category: int or None = None  # RSD record 13, 1-8
        self.tax_class_reduction: int or None = None  # RSD record 14, 0-4
        self.tax_class: int or None = None  # RSD record 15, 1-7
        self.drainage_category: int or None = None  # RSD record 16, 0-5
        self.drainage_feasibility: bool or None = None  # RSD record 17, (0 yes, 1 no)
        # RSD record 18 is unspecified and defaults to '0'
        self.drainage_year: int or None = None  # RSD record 19
        self.fertilization_year: int or None = None  # RSD record 20
        self.soil_surface_preparation_year: int or None = None  # RSD record 21
        self.natural_regeneration_feasibility: bool or None = None  # RSD record 22 (0 yes, 1 no)
        self.regeneration_area_cleaning_year: int or None = None  # RSD record 23
        self.development_class: int or None = None  # RSD record 24
        self.artificial_regeneration_year: int or None = None  # RSD record 25
        self.young_stand_tending_year: int or None = None  # RSD record 26
        self.pruning_year: int or None = None  # RSD record 27
        self.cutting_year: int or None = None  # RSD record 28
        self.forestry_centre_id: int or None = None  # RSD record 29, 0-13
        self.forest_management_category: int or None = None  # RSD record 30, 1-3,6-7
        self.method_of_last_cutting: int or None = None  # RSD record 31, 0-6
        self.municipality_id: int or None = None  # RSD record 32, code from Statistics Finland
        # RSD record 33 and 34 unused

        for key, value in d.items():
            self.__setattr__(key, value)

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
