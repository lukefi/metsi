import unittest
from copy import deepcopy
from lukefi.metsi.data.formats import vmi_const
from lukefi.metsi.data.formats.forest_builder import *
from lukefi.metsi.data.enums.internal import *
from tests.data.test_util import ForestBuilderTestBench

class TestForestBuilder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vmi12_builder = ForestBuilderTestBench.vmi12_builder
        cls.vmi13_builder = ForestBuilderTestBench.vmi13_builder

        cls.vmi12_stands = ForestBuilderTestBench.vmi12_built()
        cls.vmi13_stands = ForestBuilderTestBench.vmi13_built()

        cls.vmi12_stands_ref_trees_false = ForestBuilderTestBench.vmi12_built({'measured_trees': False, 'strata': True})
        cls.vmi13_stands_ref_trees_false = ForestBuilderTestBench.vmi13_built({'measured_trees': False, 'strata': True})


    def test_vmi12_init(self):
        vmi12_builder = self.vmi12_builder()
        self.assertEqual(4, len(vmi12_builder.forest_stands))
        self.assertEqual(1, len(vmi12_builder.reference_trees))
        self.assertEqual(2, len(vmi12_builder.tree_strata))

    def test_vmi12_stands(self):
        self.assertEqual(4, len(self.vmi12_stands))

    def test_vmi12_stand_identifiers(self):
        self.assertEqual('0-999-999-99-1', self.vmi12_stands[0].identifier)
        self.assertEqual('0-999-999-98-1', self.vmi12_stands[1].identifier)

    def test_vmi12_stand_variables(self):
        # test data coincides with county 21
        reference_area = round(vmi_const.vmi12_county_areas[21], 4)
        self.assertEqual(False, self.vmi12_stands[0].auxiliary_stand)
        self.assertEqual(True, self.vmi12_stands[3].auxiliary_stand)
        self.assertEqual(reference_area, self.vmi12_stands[0].area)
        self.assertEqual(reference_area, self.vmi12_stands[1].area)
        #auxiliary stand area should be 0
        self.assertEqual(0.0, self.vmi12_stands[3].area)
        self.assertEqual(reference_area, self.vmi12_stands[0].area_weight)
        self.assertEqual(reference_area, self.vmi12_stands[1].area_weight)
        self.assertAlmostEqual(reference_area, self.vmi12_stands[3].area_weight)

        # lat 6656996, lon 3102608, height
        self.assertEqual((6652133.0, 3246174.0, None, 'EPSG:2393'), self.vmi12_stands[0].geo_location)
        # lat 6675011, lon 3118967, height 124
        self.assertEqual((6652133.0, 3246174.0, 12.4, 'EPSG:2393'), self.vmi12_stands[1].geo_location)
        # '' -> None
        self.assertEqual(None, self.vmi12_stands[0].degree_days)
        # '1271' -> 1271.0
        self.assertEqual(1271.0, self.vmi12_stands[1].degree_days)
        # owner group is '0', which translated to 0
        self.assertEqual(OwnerCategory.UNKNOWN, self.vmi12_stands[0].owner_category)
        # owner group is '1', which translated to 0
        self.assertEqual(OwnerCategory.PRIVATE, self.vmi12_stands[1].owner_category)
        self.assertEqual(' ', self.vmi12_stands[0].fra_category)
        self.assertEqual('1', self.vmi12_stands[1].fra_category)
        self.assertEqual(LandUseCategory.SEA, self.vmi12_stands[0].land_use_category)
        self.assertEqual(LandUseCategory.FOREST, self.vmi12_stands[1].land_use_category)
        self.assertEqual('0', self.vmi12_stands[0].land_use_category_detail)
        self.assertEqual('0', self.vmi12_stands[1].land_use_category_detail)
        # paatyyppi is ' '
        self.assertEqual(None, self.vmi12_stands[0].soil_peatland_category)
        # paatyyppi is '1'
        self.assertEqual(1.0, self.vmi12_stands[1].soil_peatland_category)
        # kasvupaikkatunnus is ' '
        self.assertEqual(None, self.vmi12_stands[0].site_type_category)
        # kasvupaikkatunnus is '3'
        self.assertEqual(3, self.vmi12_stands[1].site_type_category)
        # '' -> 0
        self.assertEqual(0, self.vmi12_stands[0].tax_class)
        # '1' -> 2
        self.assertEqual(2, self.vmi12_stands[1].tax_class)
        # ojitus_tilanne is ' '
        self.assertEqual(None, self.vmi12_stands[0].drainage_category)
        # ojitus_tilanne is '0' and paatyyppi is '1'
        self.assertEqual(DrainageCategory.UNDRAINED_MINERAL_SOIL_OR_MIRE, self.vmi12_stands[1].drainage_category)
        # ojitus_aika is ''
        self.assertEqual(None, self.vmi12_stands[0].drainage_year)
        # ojitus_aika is ''
        self.assertEqual(None, self.vmi12_stands[1].drainage_year)
        # value not available in VMI12 source
        self.assertEqual(None, self.vmi12_stands[0].fertilization_year)
        # value not available in VMI12 source
        self.assertEqual(None, self.vmi12_stands[1].fertilization_year)
        # ojitus_tarve is ' '
        self.assertEqual(False, self.vmi12_stands[0].drainage_feasibility)
        # ojitus_tarve is '0'
        self.assertEqual(False, self.vmi12_stands[1].drainage_feasibility)
        # '', 2018 -> None
        self.assertEqual(None, self.vmi12_stands[0].soil_surface_preparation_year)
        # '0', 2018 -> 2018
        self.assertEqual(2018, self.vmi12_stands[1].soil_surface_preparation_year)
        # hakkuuehdotus is '  '
        self.assertEqual(False, self.vmi12_stands[0].natural_regeneration_feasibility)
        # hakkuuehdotus is '0 '
        self.assertEqual(False, self.vmi12_stands[1].natural_regeneration_feasibility)
        # muu_toimenpide is ' '
        # muu_toimenpide_aika is ' '
        # date is 020618
        self.assertEqual(None, self.vmi12_stands[0].regeneration_area_cleaning_year)
        # muu_toimenpide is '0'
        # muu_toimenpide_aika is ' '
        # date is 280818
        self.assertEqual(None, self.vmi12_stands[1].regeneration_area_cleaning_year)
        # kehitysluokka is ' ' -> 0
        self.assertEqual(0, self.vmi12_stands[0].development_class)
        # kehitysluokka is '5' -> 5
        self.assertEqual(5, self.vmi12_stands[1].development_class)
        # viljely is ' '
        # viljely_aika is ' '
        # date is 020618 and year is 2018 when date string is parsed
        self.assertEqual(None, self.vmi12_stands[0].artificial_regeneration_year)
        # viljely is '0'
        # viljely_aika is ' '
        # date is 280818 and year is 2018 when date string is parsed
        self.assertEqual(None, self.vmi12_stands[1].artificial_regeneration_year)
        # hakkuu_aika is ' ', hakkuu_tapa is ' ' (no record)
        self.assertEqual(None, self.vmi12_stands[0].young_stand_tending_year)
        # hakkuu_aika is '6', hakkuu_tapa is '4' (cutting 7 years ago)
        self.assertEqual(None, self.vmi12_stands[1].young_stand_tending_year)
        # hakkuu_aika is ' ', hakkuu_tapa is ' ' (no record)
        self.assertEqual(None, self.vmi12_stands[0].cutting_year)
        # hakkuu_aika is '6', hakkuu_tapa is '4' (cutting 7 years ago)
        self.assertEqual(2011, self.vmi12_stands[1].cutting_year)
        # forestry_centre is '00'
        self.assertEqual(0, self.vmi12_stands[0].forestry_centre_id)
        # forestry_centre is '00'
        self.assertEqual(0, self.vmi12_stands[1].forestry_centre_id)
        # fmc is '1'
        self.assertEqual(1, self.vmi12_stands[0].forest_management_category)
        # fmc is '1'
        self.assertEqual(1, self.vmi12_stands[1].forest_management_category)
        # hakkuu_tapa is ' ', (no record)
        self.assertEqual(None, self.vmi12_stands[0].method_of_last_cutting)
        # hakkuu_tapa is '4', (cutting)
        self.assertEqual(1, self.vmi12_stands[1].method_of_last_cutting)
        # municipality is '417', kitukunta is '417'
        self.assertEqual(417, self.vmi12_stands[0].municipality_id)
        # municipality is '417', kitukunta is '417'
        self.assertEqual(417, self.vmi12_stands[1].municipality_id)
        # osuus564 is '10', koealaosuudet is '10'
        self.assertEqual((1.0, 1.0), self.vmi12_stands[0].area_weight_factors)
        # osuus564 is '10', koealaosuudet is '10'
        self.assertEqual((1.0, 1.0), self.vmi12_stands[1].area_weight_factors)
        self.assertEqual(False, self.vmi12_stands[0].auxiliary_stand)
        self.assertEqual(False, self.vmi12_stands[1].auxiliary_stand)
        self.assertEqual(None, self.vmi12_stands[0].basal_area)
        self.assertEqual(19.0, self.vmi12_stands[1].basal_area)
        # vallitsevanjakson_d13ika is '   ' vallitsevanjakson_ikalisays is '  ' -> result to 0.0
        self.assertEqual(0.0, self.vmi12_stands[0].dominant_storey_age)
        # vallitsevanjakson_d13ika is '045' vallitsevanjakson_ikalisays is '06' -> result to 51.0
        self.assertEqual(51.0, self.vmi12_stands[1].dominant_storey_age)

    def test_vmi12_trees(self):
        self.assertEqual(0, len(self.vmi12_stands[0].reference_trees_pre_vec))
        self.assertEqual(1, len(self.vmi12_stands[1].reference_trees_pre_vec))
        self.assertEqual(0, len(self.vmi12_stands[2].reference_trees_pre_vec))

        # Trees with back reference to stand
        self.assertEqual(self.vmi12_stands[1], self.vmi12_stands[1].reference_trees_pre_vec[0].stand)
        self.assertEqual('0-999-999-98-1-001-tree', self.vmi12_stands[1].reference_trees_pre_vec[0].identifier)

    def test_vmi12_tree_variables(self):
        tree = self.vmi12_stands[1].reference_trees_pre_vec[0]
        # '7' -> '7'
        self.assertEqual('7', tree.tree_category)
        # '1' -> 1
        self.assertEqual(TreeSpecies.PINE, tree.species)
        # '207' -> 20.7
        self.assertEqual(20.7, tree.breast_height_diameter)
        # '1741' -> 17.41
        self.assertEqual(17.41, tree.height)
        self.assertEqual(None, tree.measured_height)
        # diameter 20.7, area factors 1.0
        self.assertEqual(39.298, tree.stems_per_ha)

        # No source value established for these. Placeholders for now.
        self.assertEqual(None, tree.saw_log_volume_reduction_factor)
        self.assertEqual(0, tree.pruning_year)
        self.assertEqual(0, tree.age_when_10cm_diameter_at_breast_height)
        self.assertEqual(0, tree.origin)
        self.assertEqual((0.0, 0.0, 0.0), tree.stand_origin_relative_position)

        #tree id source value 1
        self.assertEqual(1, tree.tree_number)

        # breast_height_age is '' -> None
        self.assertEqual(None, tree.breast_height_age)
        # age_increase is '', total_age is '', breast_height_age is '' -> 0.0
        self.assertEqual(None, tree.biological_age)
        # living_branches_height is '' -> 0.0
        self.assertEqual(0.0, tree.lowest_living_branch_height)
        # latvuskerros is '2' -> 1
        self.assertEqual(1, tree.management_category)
        self.assertEqual(Storey.DOMINANT, tree.storey)
        self.assertEqual(None, tree.tree_type)
        self.assertEqual(None, tree.tuhon_ilmiasu)

    def test_vmi12_strata(self):
        self.assertEqual(0, len(self.vmi12_stands_ref_trees_false[0].tree_strata_pre_vec))
        self.assertEqual(1, len(self.vmi12_stands_ref_trees_false[1].tree_strata_pre_vec))

        # Strata with back reference to stand
        self.assertEqual(self.vmi12_stands_ref_trees_false[1], self.vmi12_stands_ref_trees_false[1].tree_strata_pre_vec[0].stand)
        self.assertEqual('0-999-999-98-1-01-stratum', self.vmi12_stands_ref_trees_false[1].tree_strata_pre_vec[0].identifier)

    def test_vmi12_stratum(self):
        stratum = self.vmi12_stands_ref_trees_false[1].tree_strata_pre_vec[0]
        # species is '1' -> 1
        self.assertEqual(TreeSpecies.PINE, stratum.species)
        # mean_diameter is '24' (cm) -> 24.0 (cm)
        self.assertEqual(24.0, stratum.mean_diameter)
        # mean_height is '190' (dm) -> 19.0 (m)
        self.assertEqual(19.0, stratum.mean_height)
        # stemps_per_ha is '     ' -> 0.0
        self.assertEqual(0.0, stratum.stems_per_ha)
        # breast_height_age is '046' -> 46.0
        self.assertEqual(46.0, stratum.breast_height_age)
        # origin is '1' -> 0
        self.assertEqual(0, stratum.origin)
        # biological_age is '06' -> 52.0; (biological_age + breast_height_age = 52.0)
        self.assertEqual(52.0, stratum.biological_age)
        # basal area is '17' -> 17.0
        self.assertEqual(17.0, stratum.basal_area)
        self.assertEqual(Storey.DOMINANT, stratum.storey)
        self.assertEqual(1, stratum.tree_number)

    def test_vmi13_init(self):
        vmi13_builder = self.vmi13_builder()
        self.assertEqual(4, len(vmi13_builder.forest_stands))
        self.assertEqual(6, len(vmi13_builder.reference_trees))
        self.assertEqual(3, len(vmi13_builder.tree_strata))

    def test_vmi13_stands(self):
        self.assertEqual(4, len(self.vmi13_stands))

    def test_vmi13_stand_identifiers(self):
        self.assertEqual('0-1-12-1-1', self.vmi13_stands[0].identifier)
        self.assertEqual('0-2-23-2-1', self.vmi13_stands[1].identifier)

    def test_vmi13_stand_variables(self):
        # When county is 21, lohkomuoto is 0 and lohkotarkenne is 0 reference_area is 164.2650475 
        reference_area = 164.2650475
        self.assertEqual(False, self.vmi13_stands[0].auxiliary_stand)
        self.assertEqual(True, self.vmi13_stands[2].auxiliary_stand)
        self.assertEqual(reference_area, self.vmi13_stands[0].area)
        self.assertEqual(reference_area, self.vmi13_stands[1].area)
        #auxiliary stand area should be 0
        self.assertEqual(0.0, self.vmi13_stands[2].area)
        self.assertEqual(reference_area, self.vmi13_stands[0].area_weight)
        self.assertEqual(reference_area, self.vmi13_stands[1].area_weight)
        self.assertEqual(reference_area, self.vmi13_stands[2].area_weight)
        # lat 5514200.0, lon 493729.0, height None
        self.assertEqual((5514200.0, 493729.0, None, 'EPSG:3067'), self.vmi13_stands[0].geo_location)
        # lat 6671298.0, lon 1385598.0, height 124.0
        self.assertEqual((6671298.0, 1385598.0, 124.0, 'EPSG:3067'), self.vmi13_stands[1].geo_location)
        self.assertEqual(None, self.vmi13_stands[0].degree_days)
        self.assertEqual(1271.0, self.vmi13_stands[1].degree_days)
        # owner group is '4' which translates to 2
        self.assertEqual(OwnerCategory.UNKNOWN, self.vmi13_stands[0].owner_category)
        # owner group is '1' which translated to 0
        self.assertEqual(OwnerCategory.PRIVATE, self.vmi13_stands[1].owner_category)
        self.assertEqual(None, self.vmi13_stands[0].fra_category)
        self.assertEqual('1', self.vmi13_stands[1].fra_category)
        self.assertEqual(LandUseCategory.SEA, self.vmi13_stands[0].land_use_category)
        self.assertEqual(1, self.vmi13_stands[1].land_use_category)
        self.assertEqual('0', self.vmi13_stands[0].land_use_category_detail)
        self.assertEqual('0', self.vmi13_stands[1].land_use_category_detail)
        # paatyyppi is '.'
        self.assertEqual(None, self.vmi13_stands[0].soil_peatland_category)
        # paatyyppi is '1'
        self.assertEqual(1.0, self.vmi13_stands[1].soil_peatland_category)
        # kasvupaikkatunnus is '.'
        self.assertEqual(None, self.vmi13_stands[0].site_type_category)
        # kasvupaikkatunnus is '3'
        self.assertEqual(3, self.vmi13_stands[1].site_type_category)
        # '0' -> 0
        self.assertEqual(0, self.vmi13_stands[0].tax_class_reduction)
        # '0' -> 0
        self.assertEqual(0, self.vmi13_stands[1].tax_class_reduction)
        self.assertEqual(0, self.vmi13_stands[0].tax_class)
        # '1' -> 2
        self.assertEqual(2, self.vmi13_stands[1].tax_class)
        self.assertEqual(None, self.vmi13_stands[0].drainage_category)
        # ojitus_tilanne is '0' and paatyyppi is '1'
        self.assertEqual(DrainageCategory.UNDRAINED_MINERAL_SOIL_OR_MIRE, self.vmi13_stands[1].drainage_category)
        self.assertEqual(None, self.vmi13_stands[0].drainage_year)
        # ojitus_aika is '.'
        self.assertEqual(None, self.vmi13_stands[1].drainage_year)
        # value not available in VMI13 source
        self.assertEqual(None, self.vmi13_stands[0].fertilization_year)
        # value not available in VMI13 source
        self.assertEqual(None, self.vmi13_stands[1].fertilization_year)
        self.assertEqual(False, self.vmi13_stands[0].drainage_feasibility)
        # ojitus_tarve is '0'
        self.assertEqual(False, self.vmi13_stands[1].drainage_feasibility)
        self.assertEqual(None, self.vmi13_stands[0].soil_surface_preparation_year)
        self.assertEqual(2018, self.vmi13_stands[1].soil_surface_preparation_year)
        # hakkuuehdotus is '.'
        self.assertEqual(False, self.vmi13_stands[0].natural_regeneration_feasibility)
        # hakkuuehdotus is '.'
        self.assertEqual(False, self.vmi13_stands[1].natural_regeneration_feasibility)
        # muu_toimenpide is '.'
        # muu_toimenpide_aika is '0'
        # date is '20200522'
        self.assertEqual(None, self.vmi13_stands[0].regeneration_area_cleaning_year)
        # muu_toimenpide is '2'
        # muu_toimenpide_aika is '0'
        # date is 20200503
        self.assertEqual(None, self.vmi13_stands[1].regeneration_area_cleaning_year)
        self.assertEqual(0, self.vmi13_stands[0].development_class)
        self.assertEqual(5, self.vmi13_stands[1].development_class)
        self.assertEqual(None, self.vmi13_stands[0].artificial_regeneration_year)
        self.assertEqual(None, self.vmi13_stands[1].artificial_regeneration_year)
        # hakkuu_aika is 'A', hakkuu_tapa is '0' (no operation within 10 years, A is 20 years ago)
        self.assertEqual(None, self.vmi13_stands[0].young_stand_tending_year)
        self.assertEqual(None, self.vmi13_stands[1].young_stand_tending_year)
        # hakkuu_aika is 'A', hakkuu_tapa is '0' (no operation within 10 years, A is 20 years ago)
        self.assertEqual(None, self.vmi13_stands[0].cutting_year)
        self.assertEqual(2011, self.vmi13_stands[1].cutting_year)
        self.assertEqual(0, self.vmi13_stands[0].forestry_centre_id)
        self.assertEqual(0, self.vmi13_stands[1].forestry_centre_id)
        # fmc is '1'
        self.assertEqual(1, self.vmi13_stands[0].forest_management_category)
        # fmc is '1'
        self.assertEqual(1, self.vmi13_stands[1].forest_management_category)
        # hakkuu_tapa is '0' (no operation)
        self.assertEqual(None, self.vmi13_stands[0].method_of_last_cutting)
        self.assertEqual(1, self.vmi13_stands[1].method_of_last_cutting)
        self.assertEqual(417, self.vmi13_stands[0].municipality_id)
        self.assertEqual(417, self.vmi13_stands[1].municipality_id)
        self.assertEqual((0.0, 1.0), self.vmi13_stands[0].area_weight_factors)
        self.assertEqual((0.0, 1.0), self.vmi13_stands[1].area_weight_factors)
        self.assertEqual(False, self.vmi13_stands[0].auxiliary_stand)
        self.assertEqual(False, self.vmi13_stands[1].auxiliary_stand)
        self.assertEqual(None, self.vmi13_stands[0].basal_area)
        self.assertEqual(19.0, self.vmi13_stands[1].basal_area)
        self.assertEqual(0.0, self.vmi13_stands[0].dominant_storey_age)
        self.assertEqual(51.0, self.vmi13_stands[1].dominant_storey_age)

    def test_vmi13_trees(self):
        self.assertEqual(0, len(self.vmi13_stands[0].reference_trees_pre_vec))
        self.assertEqual(3, len(self.vmi13_stands[1].reference_trees_pre_vec))

        # Trees with back reference to stand
        self.assertEqual(self.vmi13_stands[1], self.vmi13_stands[1].reference_trees_pre_vec[0].stand)
        self.assertEqual('0-2-23-2-1-1-tree', self.vmi13_stands[1].reference_trees_pre_vec[0].identifier)

    def test_vmi13_tree_variables(self):
        tree = self.vmi13_stands[1].reference_trees_pre_vec[0]
        # '7' -> '7'
        self.assertEqual('7', tree.tree_category)
        # '1' -> 1
        self.assertEqual(TreeSpecies.PINE, tree.species)
        # '207' -> 20.7
        self.assertEqual(20.7, tree.breast_height_diameter)
        # '1741' -> 17.41
        self.assertEqual(17.41, tree.height)
        self.assertEqual(None, tree.measured_height)
        # missing value normalized to None
        self.assertEqual(None, None)
        # diameter 25, area factors 1.0
        self.assertEqual(39.298, tree.stems_per_ha)

        # No source value established for these. Placeholders for now.
        self.assertEqual(None, tree.saw_log_volume_reduction_factor)
        self.assertEqual(0, tree.pruning_year)
        self.assertEqual(0, tree.age_when_10cm_diameter_at_breast_height)
        self.assertEqual(0, tree.origin)
        self.assertEqual((0.0, 0.0, 0.0), tree.stand_origin_relative_position)

        #tree id source value 1
        self.assertEqual(1, tree.tree_number)

        # breast_height_age is '.' -> None
        self.assertEqual(None, tree.breast_height_age)
        # age_increase is '.', total_age is '.', breast_height_age is '.' -> None
        self.assertEqual(None, tree.biological_age)
        # living_branches_height is '.' -> 0.0
        self.assertEqual(0.0, tree.lowest_living_branch_height)
        # latvuskerros is '2' -> 1
        self.assertEqual(1, tree.management_category)
        self.assertEqual(Storey.DOMINANT, tree.storey)
        self.assertEqual(None, tree.tree_type)
        self.assertEqual(None, tree.tuhon_ilmiasu)

    def test_vmi13_strata(self):
        self.assertEqual(0, len(self.vmi13_stands_ref_trees_false[0].tree_strata_pre_vec))
        self.assertEqual(2, len(self.vmi13_stands_ref_trees_false[1].tree_strata_pre_vec))

        # Strata with back reference to stand
        self.assertEqual(self.vmi13_stands_ref_trees_false[1], self.vmi13_stands_ref_trees_false[1].tree_strata_pre_vec[0].stand)
        self.assertEqual('0-2-23-2-1-1-stratum', self.vmi13_stands_ref_trees_false[1].tree_strata_pre_vec[0].identifier)

    def test_vmi13_stratum(self):
        stratum = self.vmi13_stands_ref_trees_false[1].tree_strata_pre_vec[0]
        # species is 1 -> 1
        self.assertEqual(TreeSpecies.PINE, stratum.species)
        # mean_diameter is '24' (cm) -> 24.0 (cm)
        self.assertEqual(24.0, stratum.mean_diameter)
        # mean_height is '19' (dm) -> 19.0 (m)
        self.assertEqual(19.0, stratum.mean_height)
        # stems_per_ha is '.' -> 0
        self.assertEqual(0, stratum.stems_per_ha)
        # breast_height_age is '46' -> 46.0
        self.assertEqual(46.0, stratum.breast_height_age)
        # origin is '1' -> 0
        self.assertEqual(0, stratum.origin)
        # biological_age is '52' -> 52.0
        self.assertEqual(52.0, stratum.biological_age)
        # basal area is '17' -> 17.0
        self.assertEqual(17.0, stratum.basal_area)
        self.assertEqual(Storey.DOMINANT, stratum.storey)
        self.assertEqual(1, stratum.tree_number)


    def test_remove_strata(self):
        stands = deepcopy(self.vmi13_stands)
        self.vmi13_builder().remove_strata(stands)
        self.assertEqual(0, len(stands[1].tree_strata_pre_vec))

