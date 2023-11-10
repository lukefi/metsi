from collections.abc import Sequence, Iterable
import xml.etree.ElementTree as ET
from pandas import DataFrame, Series

from lukefi.metsi.data.enums.internal import OwnerCategory
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.data.conversion import vmi2internal, fc2internal
from lukefi.metsi.data.formats import smk_util, util, vmi_util, gpkg_util
from abc import ABC, abstractmethod
from lukefi.metsi.data.formats.vmi_const import VMI12StandIndices, VMI12TreeIndices, VMI12StratumIndices, \
    VMI13StandIndices, VMI13TreeIndices, VMI13StratumIndices

class ForestBuilder(ABC):
    """Abstract base class of forest builders"""

    @abstractmethod
    def build(self) -> list[ForestStand]:
        ...


class VMIBuilder(ForestBuilder):
    """Shared functionality of VMI* builders"""

    def __init__(self, builder_flags: dict, data_rows: iter):
        """
        Initialize instance variable lists for forest stands, reference trees and tree strata.
        Given source data is pre-parsed for data types 1, 2 and 3.

        :param builder_flags: building process spesific flags
        :param data_rows: Iterable raw data rows from a VMI source file
        """
        self.forest_stands: list[str] = []
        self.reference_trees: list[str] = []
        self.tree_strata: list[str] = []
        self.builder_flags = builder_flags

        for row in data_rows:
            try:
                row_type = self.find_row_type(row)
                if row_type == 1:
                    self.forest_stands.append(row)
                elif row_type == 2:
                    self.tree_strata.append(row)
                elif row_type == 3:
                    self.reference_trees.append(row)
            except (IndexError, TypeError) as e:
                print(e)
                print('warning: VMI row not addressable: ')
                print('    ' + str(row))

    def convert_stand_entry(self, indices: VMI12StandIndices or VMI13StandIndices,
                            data_row: Sequence, stand_id: int or None = None) -> ForestStand:
        """Create a ForestStand out of given VMI type 1 data row using given data indices and order number"""
        result = ForestStand()
        result.identifier = vmi_util.generate_stand_identifier(data_row, indices)
        result.set_identifiers(stand_id)
        result.degree_days = vmi_util.transform_vmi_degree_days(data_row[indices.degree_days])
        result.owner_category = vmi2internal.convert_owner(data_row[indices.owner_group])
        result.fra_category = data_row[indices.fra_class]
        result.land_use_category = vmi2internal.convert_land_use_category(data_row[indices.land_category])
        result.land_use_category_detail = data_row[indices.land_category_detail]
        result.site_type_category = vmi2internal.convert_site_type_category(data_row[indices.kasvupaikkatunnus])
        result.soil_peatland_category = vmi2internal.convert_soil_peatland_category(data_row[indices.paatyyppi])
        result.tax_class_reduction = vmi_util.determine_tax_class_reduction(data_row[indices.tax_class_reduction])
        result.tax_class = vmi_util.determine_tax_class(data_row[indices.tax_class])
        result.drainage_category = vmi2internal.convert_drainage_category(data_row[indices.ojitus_tilanne])
        result.development_class = vmi_util.determine_development_class(data_row[indices.kehitysluokka])
        result.drainage_feasibility = vmi_util.determine_drainage_feasibility(data_row[indices.ojitus_tarve])
        result.forestry_centre_id = vmi_util.parse_forestry_centre(data_row[indices.forestry_centre])
        result.forest_management_category = vmi_util.determine_forest_management_category(
            result.land_use_category,
            result.forestry_centre_id,
            data_row,
            result.owner_category,
            indices, False)
        result.municipality_id = vmi_util.determine_municipality(
            data_row[indices.municipality],
            data_row[indices.kitukunta])
        result.natural_regeneration_feasibility = vmi_util.determine_natural_renewal(data_row[indices.hakkuuehdotus])
        result.auxiliary_stand = data_row[indices.stand_number] != '1'
        result.basal_area = util.parse_type(data_row[indices.pohjapintaala], float)
        return result

    def convert_tree_entry(self, indices: VMI12TreeIndices or VMI13TreeIndices,
                           data_row: Sequence) -> ReferenceTree:
        result = ReferenceTree()
        result.tree_category = data_row[indices.tree_category]
        result.identifier = vmi_util.generate_tree_identifier(data_row, indices)
        result.species = vmi2internal.convert_species(data_row[indices.species])
        result.breast_height_diameter = vmi_util.transform_tree_diameter(data_row[indices.diameter])
        result.breast_height_age, result.biological_age = vmi_util.determine_tree_age_values(
            data_row[indices.d13_age],
            data_row[indices.age_increase],
            data_row[indices.total_age])
        result.pruning_year = 0
        result.age_when_10cm_diameter_at_breast_height = 0
        result.origin = 0
        result.tree_number = util.parse_type(data_row[indices.tree_number], int)
        result.stand_origin_relative_position = (0.0, 0.0, 0.0)
        result.lowest_living_branch_height = util.get_or_default(
            util.parse_type(data_row[indices.living_branches_height], float),
            0.0) / 10.0
        result.management_category = vmi_util.determine_tree_management_category(data_row[indices.latvuskerros])
        result.storey = vmi_util.determine_storey_for_tree(data_row[indices.latvuskerros])
        result.tree_type = vmi_util.determine_tree_type(data_row[indices.tree_type])
        result.tuhon_ilmiasu = None if data_row[indices.tuhon_ilmiasu] == "  " else data_row[indices.tuhon_ilmiasu]
        return result

    def convert_stratum_entry(self, indices: VMI12StratumIndices or VMI13StratumIndices,
                              data_row: Sequence) -> TreeStratum:
        result = TreeStratum()
        result.identifier = vmi_util.generate_stratum_identifier(data_row, indices)
        result.species = vmi2internal.convert_species(data_row[indices.species])
        result.origin = vmi_util.determine_stratum_origin(data_row[indices.origin])
        result.stems_per_ha = util.get_or_default(
            util.parse_type(data_row[indices.stems_per_ha], float), 0.0)
        result.sapling_stems_per_ha = util.get_or_default(
            util.parse_type(data_row[indices.sapling_stems_per_ha], float), 0.0)
        result.sapling_stratum = result.has_sapling_stems_per_ha()
        result.mean_diameter = util.parse_type(data_row[indices.avg_diameter], float)
        result.mean_height = vmi_util.determine_stratum_tree_height(data_row[indices.avg_height])
        (biological_age, breast_height_age) = vmi_util.determine_stratum_age_values(
            data_row[indices.biological_age],
            data_row[indices.d13_age],
            result.mean_height)
        result.breast_height_age = breast_height_age
        result.biological_age = biological_age
        result.basal_area = util.parse_type(data_row[indices.basal_area], float)
        result.cutting_year = 0
        result.age_when_10cm_diameter_at_breast_height = 0
        result.tree_number = 0
        result.stand_origin_relative_position = (0.0, 0.0, 0.0)
        result.lowest_living_branch_height = 0.0
        result.management_category = 1
        result.storey = vmi_util.determine_storey_for_stratum(data_row[indices.stratum_rank])
        return result

    def remove_strata(self, stands: list[ForestStand]):
        """Empties the stands' `tree_strata` lists."""
        return [stand.tree_strata.clear() for stand in stands]

    @abstractmethod
    def find_row_type(self, row: Iterable):
        ...

    @abstractmethod
    def build(self) -> list[ForestStand]:
        ...


class VMI12Builder(VMIBuilder):
    """VMI12 specific builder implementation"""

    def __init__(self, builder_flags: dict, data_rows: list[str] = []):
        # TODO: data_rows sanity check for VMI12
        super().__init__(builder_flags, data_rows)

    def convert_stand_entry(self, indices: VMI12StandIndices, data_row: Sequence,
                            stand_id: int or None = None) -> ForestStand:
        """Create a ForestStand out of given VMI12 type 1 data row using given data indices and order number"""
        result = super().convert_stand_entry(indices, data_row, stand_id)
        result.year = vmi_util.parse_vmi12_date(data_row[indices.date]).year
        area_ha = vmi_util.determine_vmi12_area_ha(
            int(data_row[indices.lohkomuoto]),
            int(data_row[indices.county]))
        result.area_weight_factors = vmi_util.determine_area_factors(
            data_row[indices.osuus5m],
            data_row[indices.osuus9m]
        )
        result.set_area(area_ha)
        lat = util.parse_type(data_row[indices.lat], float)
        lon = util.parse_type(data_row[indices.lon], float)
        height = vmi_util.transform_vmi12_height_above_sea_level(data_row[indices.height_above_sea_level])
        result.set_geo_location(lat, lon, height, "EPSG:2393")
        result.drainage_year = vmi_util.determine_drainage_year(data_row[indices.ojitus_aika], result.year)
        result.soil_surface_preparation_year = vmi_util.determine_soil_surface_preparation_year(
                    data_row[indices.maanmuokkaus],
                    result.year)
        result.regeneration_area_cleaning_year = vmi_util.determine_clearing_of_reform_sector_year(
                    data_row[indices.muu_toimenpide],
                    data_row[indices.muu_toimenpide_aika],
                    result.year)
        result.artificial_regeneration_year = vmi_util.determine_artificial_regeneration_year(
            data_row[indices.viljely],
            data_row[indices.viljely_aika],
            result.year)
        maintenance_details = vmi_util.determine_forest_maintenance_details(
            data_row[indices.hakkuu_tapa],
            data_row[indices.hakkuu_aika],
            result.year
        )
        result.young_stand_tending_year = maintenance_details[0]
        result.cutting_year = maintenance_details[1]
        result.method_of_last_cutting = maintenance_details[2]
        return result

    def convert_tree_entry(self, indices: VMI12TreeIndices, data_row: Sequence):
        result = super().convert_tree_entry(indices, data_row)
        result.height = vmi_util.determine_tree_height(data_row[indices.height], conversion_factor=100.0)
        result.measured_height = vmi_util.determine_tree_height(data_row[indices.measured_height], conversion_factor=10.0)
        result.stems_per_ha = vmi_util.determine_stems_per_ha(result.breast_height_diameter, True)
        return result

    def find_row_type(self, row: str):
        """Return VMI12 data type of the row"""
        return int(row[13])


    def build(self) -> list[ForestStand]:
        """Populate a list of ForestStand with associated ReferenceTree and TreeStratum entries.
        Using constructor initialized instance variables as source.

        Returns:
        list[ForestStand]:populated and parsed VMI12 forest stands with reference trees and tree strata
        """
        result: dict[str, ForestStand] = {}
        for i, row in enumerate(self.forest_stands):
            stand = self.convert_stand_entry(VMI12StandIndices, row, i + 1)
            result[stand.identifier] = stand
        if self.builder_flags['strata']:
            for i, row in enumerate(self.tree_strata):
                stratum = self.convert_stratum_entry(VMI12StratumIndices, row)
                stand_id = vmi_util.generate_stand_identifier(row, VMI12StandIndices)
                stand = result[stand_id]
                stratum.stand = stand
                stand.tree_strata.append(stratum)

        if self.builder_flags['reference_trees']:
            for i, row in enumerate(self.reference_trees):
                tree = self.convert_tree_entry(VMI12TreeIndices, row)
                stand_id = vmi_util.generate_stand_identifier(row, VMI12StandIndices)
                stand = result[stand_id]
                tree.stand = stand
                stand.reference_trees.append(tree)
        
        return list(result.values())

class VMI13Builder(VMIBuilder):
    """VMI13 specific builder implementation"""

    def __init__(self,  builder_flags: dict, data_rows: list[str] = []):
        pre_parsed_rows = map(lambda raw: raw.split(), data_rows)
        # TODO: data_rows sanity check for VMI13
        super().__init__(builder_flags, pre_parsed_rows)

    def find_row_type(self, row: Sequence):
        """Return VMI13 data type of the row"""
        return int(row[0])

    def convert_stand_entry(self, indices: VMI13StandIndices,
                            data_row: Sequence,
                            stand_id: int or None = None) -> ForestStand:
        """Create a ForestStand out of given VMI13 type 1 data row using given data indices and order number"""
        result = super().convert_stand_entry(indices, data_row, stand_id)
        result.year = vmi_util.parse_vmi13_date(data_row[indices.date]).year
        area_ha = vmi_util.determine_vmi13_area_ha(int(data_row[indices.lohkomuoto]))
        result.area_weight_factors = vmi_util.determine_area_factors(
            data_row[indices.osuus4m],
            data_row[indices.osuus9m]
        )
        result.set_area(area_ha)
        lat = util.parse_type(data_row[indices.lat], float)
        lon = util.parse_type(data_row[indices.lon], float)
        height = vmi_util.transform_vmi13_height_above_sea_level(data_row[indices.height_above_sea_level])
        result.set_geo_location(lat, lon, height)
        result.drainage_year = vmi_util.determine_drainage_year(data_row[indices.ojitus_aika], result.year)
        result.fertilization_year = None  # value missing in VMI12 source
        result.soil_surface_preparation_year = vmi_util.determine_soil_surface_preparation_year(
            data_row[indices.maanmuokkaus],
            result.year
        )
        result.regeneration_area_cleaning_year = vmi_util.determine_clearing_of_reform_sector_year(
            data_row[indices.muu_toimenpide],
            data_row[indices.muu_toimenpide_aika],
            result.year)
        result.artificial_regeneration_year = vmi_util.determine_artificial_regeneration_year(
            data_row[indices.viljely],
            data_row[indices.viljely_aika],
            result.year)
        maintenance_details = vmi_util.determine_forest_maintenance_details(
            data_row[indices.hakkuu_tapa],
            data_row[indices.hakkuu_aika],
            result.year)
        result.young_stand_tending_year = maintenance_details[0]
        result.cutting_year = maintenance_details[1]
        result.method_of_last_cutting = maintenance_details[2]
        return result

    def convert_tree_entry(self, indices: VMI13TreeIndices, data_row: Sequence):
        result = super().convert_tree_entry(indices, data_row)
        result.height = vmi_util.determine_tree_height(data_row[indices.height], conversion_factor=100.0)
        result.measured_height = vmi_util.determine_tree_height(data_row[indices.measured_height], conversion_factor=10.0)
        result.stems_per_ha = vmi_util.determine_stems_per_ha(result.breast_height_diameter, False)
        return result

    def build(self) -> list[ForestStand]:
        """Populate a list of ForestStand with associated ReferenceTree and TreeStratum entries.
        Using constructor initialized instance variables as source.

        Returns:
        list[ForestStand]:populated and parsed VMI13 forest stands with reference trees and tree strata
        """
        result: dict[str, ForestStand] = {}
        for i, row in enumerate(self.forest_stands):
            stand = self.convert_stand_entry(VMI13StandIndices, row, i + 1)
            result[stand.identifier] = stand

        if self.builder_flags['strata']:
            for i, row in enumerate(self.tree_strata):
                stratum = self.convert_stratum_entry(VMI13StratumIndices, row)
                stand_id = vmi_util.generate_stand_identifier(row, VMI13StandIndices)
                stand = result[stand_id]
                stratum.stand = stand
                stand.tree_strata.append(stratum)

        if self.builder_flags['reference_trees']:
            for i, row in enumerate(self.reference_trees):
                tree = self.convert_tree_entry(VMI13TreeIndices, row)
                stand_id = vmi_util.generate_stand_identifier(row, VMI13StandIndices)
                stand = result[stand_id]
                tree.stand = stand
                stand.reference_trees.append(tree)

        return list(result.values())

class XMLBuilder(ForestBuilder):

    def __init__(self, builder_flags: dict, data: str):
        self.root: ET.Element = ET.fromstring(data)
        self.builder_flags = builder_flags


    @abstractmethod
    def build(self) -> list[ForestStand]:
        ...


    @abstractmethod
    def convert_stand_entry(self):
        ...


    @abstractmethod
    def convert_stratum_entry(self):
        ...

class ForestCentreBuilder(XMLBuilder):

    xpath_strata = './ts:TreeStandData/ts:TreeStandDataDate[@type="{}"]/tst:TreeStrata/tst:TreeStratum'
    xpath_stand = "st:Stands/st:Stand"


    def __init__(self, builder_flags: dict, data: str):
        super().__init__(builder_flags, data)
        self.xpath_strata = self.xpath_strata.format(builder_flags['strata_origin'])


    def set_stand_operations(self, stand: ForestStand, operations: dict[int, tuple[int, int]]) -> ForestStand:
        for oper in operations.values():
            (oper_type, oper_year) = oper
            if oper_type in (1,):
                stand.cutting_year = oper_year # RSD record 28
                stand.method_of_last_cutting = 4 # RSD record 31
            elif oper_type in (2, 13, 20):
                stand.cutting_year = oper_year # RSD record 28
                stand.method_of_last_cutting = 3 # RSD record 31
            elif oper_type in (3, 11, 12, 14, 91, 94):
                stand.cutting_year = oper_year # RSD record 28
                stand.method_of_last_cutting = 1 # RSD record 31
            elif oper_type in (4, 15, 100):
                stand.cutting_year = oper_year # RSD record 28
                stand.method_of_last_cutting = 6 if stand.soil_peatland_category in (1,2,3) else 5
            elif oper_type in (6, 7, 102, 116, 123, 124):
                stand.cutting_year = oper_year # RSD record 28
                stand.method_of_last_cutting = 6 # RSD record 31
            elif oper_type in (8, 101, 103, 104, 105, 106, 107, 108, 109,
                110, 111, 112, 113, 114, 115, 117, 118,
                119, 120, 121, 122, 125, 126, 127, 128):
                stand.cutting_year = oper_year # RSD record 28
                stand.method_of_last_cutting = 5 # RSD record 31
            elif oper_type in (200, 201, 202, 203, 204, 205, 206, 207, 208,
                209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220,
                221, 222, 223, 224, 225, 226, 227, 228, 300, 301, 302, 303,
                304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315,
                316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327,
                328, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611,
                612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623,
                624, 625, 626, 627, 628, 629, 630):
                stand.artificial_regeneration_year = oper_year # RSD record 25
            elif oper_type in (401, 410, 420, 450):
                stand.regeneration_area_cleaning_year = oper_year # RSD record 23
            elif oper_type in (501, 510, 511, 520, 521, 522, 523, 530, 531, 540, 550, 560, 960):
                stand.soil_surface_preparation_year = oper_year # RSD record 21
            elif oper_type in (660, 670, 680, 690, 701, 730, 740, 745, 750, 760, 860, 870, 880, 890):
                stand.young_stand_tending_year = oper_year # RSD record 26
            elif oper_type in (911, 912):
                stand.fertilization_year = oper_year # RSD record 20
            elif oper_type in (930, 940):
                stand.drainage_year = oper_year # RSD record 19
            elif oper_type in (970,):
                stand.pruning_year = oper_year # RSD record 27
            else:
                UserWarning('Unable to spesify operation type {} for stand \'{}\''.format(oper_type, stand.identifier))
        return stand


    def convert_stand_entry(self, estand: ET.Element) -> ForestStand:
        stand_basic_data = smk_util.parse_stand_basic_data(estand)
        stand = ForestStand()
        stand.management_unit_id = None # RSD record 1
        stand.year = smk_util.parse_year(stand_basic_data.StandBasicDataDate) # RSD record 2
        stand.set_area(util.parse_type(stand_basic_data.Area, float)) # RSD record 3 and 4
        (latitude, longitude, crs) = smk_util.parse_coordinates(estand)
        stand.geo_location = (latitude, longitude, None, crs) # RSD record 5,6,8
        stand.identifier = stand_basic_data.id # RSD record 7
        stand.degree_days = None # RSD record 9
        # TODO: need to figure out the source for this in the XML
        stand.owner_category = OwnerCategory.PRIVATE # RSD record 10
        stand.land_use_category = fc2internal.convert_land_use_category(stand_basic_data.MainGroup) # RSD record 11
        stand.soil_peatland_category = fc2internal.convert_soil_peatland_category(stand_basic_data.SubGroup) # RSD record 12
        stand.site_type_category = fc2internal.convert_site_type_category(stand_basic_data.FertilityClass) # RSD record 13
        stand.tax_class_reduction = 0 # RSD record 14
        stand.tax_class = 0 # RSD record 15
        stand.drainage_category = fc2internal.convert_drainage_category(stand_basic_data.DrainageState) # RSD record 16
        stand.drainage_feasibility = True # RSD record 17
        # RSD record 18 is '0' by default
        operations = smk_util.parse_stand_operations(estand, target_operations='past')
        stand = self.set_stand_operations(stand, operations) # RSD records 19, 20, 21, 23, 25, 26, 27, 28 and 31
        stand.natural_regeneration_feasibility = False # RSD record 22
        stand.development_class = smk_util.parse_development_class(0) # RSD record 24
        stand.forestry_centre_id = None # RSD record 29
        stand.forest_management_category = smk_util.parse_forest_management_category(stand_basic_data.CuttingRestriction) or 1  # 30
        stand.municipality_id = None # RSD record 32
        # RSD record 33 and 34 unused
        return stand


    def convert_stratum_entry(self, estratum: ET.Element) -> TreeStratum:
        stratum_data = smk_util.parse_stratum_data(estratum)
        stratum = TreeStratum()
        stratum.identifier = util.parse_type(stratum_data.id, int)
        stratum.species = fc2internal.convert_species(stratum_data.TreeSpecies)
        stratum.stems_per_ha = util.parse_type(stratum_data.StemCount, int)
        stratum.mean_diameter = util.parse_type(stratum_data.MeanDiameter, float)
        stratum.mean_height = util.parse_type(stratum_data.MeanHeight, float)
        stratum.biological_age = util.parse_type(stratum_data.Age, float)
        stratum.basal_area = util.parse_type(stratum_data.BasalArea, float)
        stratum.tree_number = util.parse_type(stratum_data.StratumNumber, int)
        stratum.storey = fc2internal.convert_storey(stratum_data.Storey)
        return stratum


    def build(self) -> list[ForestStand]:
        stands = []
        estands = self.root.findall(self.xpath_stand, smk_util.NS)
        for estand in estands:
            stand = self.convert_stand_entry(estand)
            strata = []
            estrata = estand.findall(self.xpath_strata, smk_util.NS)
            for estratum in estrata:
                stratum = self.convert_stratum_entry(estratum)
                stratum.identifier = f"{stand.identifier}.{stratum.tree_number or stratum.identifier}-stratum"
                stratum.stand = stand
                strata.append(stratum)
            stand.tree_strata = strata
            stand.basal_area = smk_util.calculate_stand_basal_area(stand.tree_strata)
            stands.append(stand)
        return stands


class GeoPackageBuilder(ForestBuilder):
    """ ForestBuilder class for geopackage format spesification """
    stands: DataFrame = None
    strata: DataFrame = None
    type_value = None

   
    def __init__(self, builder_flags: dict, db_path: str):
        """ Reads Geopackage format into pandas dataframe representing stands and strata """
        self.type_value = builder_flags['strata_origin']
        (self.stands,
         self.strata) = gpkg_util.read_geopackage(db_path, self.type_value)


    def convert_stand_entry(self, entry: Series) -> ForestStand:
        """ Converts a single pandas Series object into a ForestStand object
        :return: ForestStand object
        """
        stand = ForestStand()
        stand.management_unit_id = None # RSD record 1
        stand.year = smk_util.parse_year(entry.date) # RSD record 2
        stand.set_area(entry.area - entry.areadecrease) # RSD record 3 and 4
        # RSD records 5, 6 and 8
        (latitude, longitude) = entry.centroid.get('centroid')
        stand.geo_location = (latitude,
                              longitude,
                              None,
                              entry.centroid.get('crs'))
        stand.identifier = entry.standid # RSD record 7
        stand.degree_days = None # RSD record 9
        stand.owner_category = OwnerCategory.PRIVATE # RSD record 10
        stand.land_use_category = fc2internal.convert_land_use_category(util.parse_type(entry.maingroup, str)) # RSD record 11
        stand.soil_peatland_category = fc2internal.convert_soil_peatland_category(util.parse_type(entry.subgroup, str)) # RSD record 12
        stand.site_type_category = fc2internal.convert_site_type_category(util.parse_type(entry.fertilityclass, str)) # RSD record 13
        # RSD record 14
        # RSD record 15
        stand.drainage_category = fc2internal.convert_to_internal(
            util.parse_type(entry.drainagestate, int, str),
            fc2internal.convert_drainage_category) # RSD record 16
        stand.drainage_feasibility = True # RSD record 17
        # RSD record 18 is '0' by default
        # TODO: parse operations -> RSD records 19, 20, 21, 23, 25, 26, 27, 28 and 31
        stand.natural_regeneration_feasibility = False # RSD record 22
        stand.development_class = smk_util.parse_development_class(util.parse_type(entry.developmentclass, str)) # RSD record 24
        stand.forestry_centre_id = None # RSD record 29
        restrictioncode = entry.restrictioncode if entry.restrictiontype == 1 else 1
        stand.forest_management_category = smk_util.parse_forest_management_category(util.parse_type(restrictioncode, int, str)) # 30
        stand.municipality_id = None # RSD record 32
        # RSD record 33 and 34 unused
        return stand


    def convert_stratum_entry(self, entry: Series) -> TreeStratum:
        """ Converts a single pandas Series object into a TreeStratum object
        :return: TreeStratum object
        """
        stratum = TreeStratum()
        stratum.identifier = entry.treestratumid
        stratum.species = fc2internal.convert_species(util.parse_type(entry.treespecies, int, str))
        stratum.stems_per_ha = entry.stemcount
        stratum.mean_diameter = entry.meandiameter
        stratum.mean_height = entry.meanheight
        stratum.biological_age = util.parse_type(entry.age, float)
        stratum.tree_number = entry.stratumnumber
        stratum.basal_area = entry.basalarea
        stratum.storey = entry.storey
        return stratum


    def build(self) -> list[ForestStand]:
        """ Converts geopackage into list of ForestStand objects.
        :return: List of ForestStand objects 
        """
        stands = []
        for _, rowi in self.stands.iterrows():
            # for each stand row
            stand = self.convert_stand_entry(rowi)
            strata = []
            i_strata = self.strata[self.strata['standid'] == stand.identifier]
            for _, rowj in i_strata.iterrows():
                # for each strata row
                stratum = self.convert_stratum_entry(rowj)
                stratum.stand = stand
                strata.append(stratum)
            stand.tree_strata = strata
            stand.basal_area = smk_util.calculate_stand_basal_area(stand.tree_strata)
            stands.append(stand)
        return stands