from copy import deepcopy
import unittest

from lukefi.metsi.data.formats import vmi_const
from lukefi.metsi.data.formats.ForestBuilder import *
from lukefi.metsi.data.enums.internal import *

class TestForestBuilder(unittest.TestCase):

    default_builder_flags = {"measured_trees": True, "strata": True}

    @classmethod
    def vmi12_builder(cls, vmi_builder_flags: dict = default_builder_flags) -> VMI12Builder:
        vmi12_data = [
            'K0999999 99 11    66521333246174    1010   0041721         000059500417      1   0         40020618 B0          0   0 0   0              0  0                   6652133.85 C 102600.11 66521333246174                                                                                          0      0',
            'K0999999 98 11    66521333246174    1010   1141721         140259100417404   6  99  1241271S1280818 101 1 30    0   0 0   0   00  0 10   0  0   111 011004322   6652133.94 J 118950.77 66521333246174 S1 5 1         09K10E10L09M09M19           24189 04506      1298460   0 0   0 0   00 222 1      1',
            'K0999999 98 12 01  1 11             24 190  04606N17 1  84A1 0',
            'K0999999 98 13001 1207217 2  01 15521741  020081711 00                                                              7725 3999  342                                                                                                                                           259959  134571   11515 39185 101864  4303 11769  8489 24696 4196',
            'K0999999 97 11    66521333246174    1010   1117021         060059100170409   2   3  1891251S7260918 101 1 20    0   0 0   0   00  0 00   0  0   0   011004323   6652133.28 T  97955.34 66521333246174 S1 3 3         00M00M00M      00      1800 04050 00705 1000012940A    0 0   0 12  00 222 1      3   9383',
            'K0999999 97 12 01  1 31 1800 5000   04 050  00705F00 1 714B2 0',
            'K0999999 96 21    66521333246174    0100   1041721         000059100417      4  55         S0280818 101 3 4     0   0 0   0    132       0  0        1          6652133.05 T 117155.45 66521333246174    5 1                                                          0A                              3  19 21'
        ]

        vmi12_builder: VMIBuilder = VMI12Builder(vmi_builder_flags, vmi12_data)
        return vmi12_builder

    @classmethod
    def vmi13_builder(cls, vmi_builder_flags: dict = default_builder_flags) -> VMI13Builder:
        vmi13_data = [
            '1 U 1  99  99 99 1   . 0 20181121 2018 258 3 1 10 10  . 12 10 176 176 893    1    5 4 S 7013044.52 543791.23 7013044.52 543791.23  179.70 1019    . T  1 3   33 220  0   . 0  . 1 0  0  . . 0 1  0  . . 0 0 2 3 0  . 2 3 1 35 2 3 2 0 4  75 0 0 3 1 5  2 .  . .  . 15 4 10 0 15 2 10 8 15 6 26 .  .  .    . 22 187  63 19 . U     . E 1 . . 0 A . . . . 0 . 0 .  . 0 . 7 3 . . 4 1 . 2 2 2   0 . . 0 . .   1  0 0 .   . 0 0 . . .         . 1 7013044.52 543791.23 .    .',
            '3 U 1  99  99 99 1  10 0 20181121 258  11 V  1  250 7 2    .    . 306  863 1  0 0 .   .   .   .   .  . . .  .  .  .  . .  . .  . . . . . .   .   . .  .   .   .   .   . .   . . .   . . .   . . .   . . .   . . .   . . .   . . .   . . . .  . .  . .  . .  . .  . .  . .  . .  .     .     .     .     .     .     .     .     .     .        .        .        .     .       .      .      .      .      .     . .    .',
            '3 U 1  99  99 99 1  10 0 20181121 258  11 V  1  250 7 2    .    . 306  863 1  0 0 .   .   .   .   .  . . .  .  .  .  . .  . .  . . . . . .   .   . .  .   .   .   .   . .   . . .   . . .   . . .   . . .   . . .   . . .   . . .   . . . .  . .  . .  . .  . .  . .  . .  . .  .     .     .     .     .     .     .     .     .     .        .        .        .     .       .      .      .      .      .     . .    .',
            '1 U 1  99  99 98 1   . 0 20181102 2018 258 3 1 10 10  . 11  9 402 402 430    6   20 1 S 7012044.52 543491.23 7012044.52 543491.23  136.10 1084    . T  2 3   54 205  0   . 8 18 1 0  0  . . 0 1  0  . . 0 0 1 3 0  . . 0 0  . 0 . 1 0 1   5 3 2 3 1 3  2 .  . .  .  3 9  2 0  3 2  . .  . .  5 .  .  . 2150  4  35   6  8 . S 10600 E 2 7 0 1 6 0 . . . 2 A 1 A  2 0 . 1 2 . . 0 0 . 2 2 2   0 . . 0 . .   . 25 0 .   . 4 0 . . .         . 1 7012044.52 543491.23 .    .',
            '2 U 1  99  99 98 1   1 0 20181102 258 1  2 3 1350  1400  4  38 E   7  8 F  2 .  0 .  .  . .  . .    .',
            '1 U 1  99  99 98 2   . 0 20181102 2018 258 3 1 10 10  . 11  9 402 402 430    6   20 1 S 7012044.52 543491.23 7012044.52 543491.23  136.10 1084    . T  2 3   54 205  0   . 8 18 1 0  0  . . 0 1  0  . . 0 0 1 3 0  . . 0 0  . 0 . 1 0 1   5 3 2 3 1 3  2 .  . .  .  3 9  2 0  3 2  . .  . .  5 .  .  . 2150  4  35   6  8 . S 10600 E 2 7 0 1 6 0 . . . 2 A 1 A  2 0 . 1 2 . . 0 0 . 2 2 2   0 . . 0 . .   . 25 0 .   . 4 0 . . .         . 1 7012044.52 543491.23 .    .',
        ]
        vmi13_builder: VMIBuilder = VMI13Builder(vmi_builder_flags, vmi13_data)
        return vmi13_builder

    @classmethod
    def vmi12_built(cls, vmi_builder_flags: dict =default_builder_flags):
        return cls.vmi12_builder(vmi_builder_flags).build()

    @classmethod
    def vmi13_built(cls, vmi_builder_flags: dict = default_builder_flags):
        return cls.vmi13_builder(vmi_builder_flags).build()

    vmi12_stands = None
    vmi13_stands = None

    vmi12_stands_ref_trees_false = None
    vmi13_stands_ref_trees_false = None

    @classmethod
    def setUpClass(cls):
        cls.vmi12_stands = cls.vmi12_built()
        cls.vmi13_stands = cls.vmi13_built()

        cls.vmi12_stands_ref_trees_false = cls.vmi12_built({'measured_trees': False, 'strata': True})
        cls.vmi13_stands_ref_trees_false = cls.vmi13_built({'measured_trees': False, 'strata': True})


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

    def test_vmi12_trees(self):
        self.assertEqual(0, len(self.vmi12_stands[0].reference_trees))
        self.assertEqual(1, len(self.vmi12_stands[1].reference_trees))
        self.assertEqual(0, len(self.vmi12_stands[2].reference_trees))

        # Trees with back reference to stand
        self.assertEqual(self.vmi12_stands[1], self.vmi12_stands[1].reference_trees[0].stand)
        self.assertEqual('0-999-999-98-1-001-tree', self.vmi12_stands[1].reference_trees[0].identifier)

    def test_vmi12_tree_variables(self):
        tree = self.vmi12_stands[1].reference_trees[0]
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
        self.assertEqual(0, len(self.vmi12_stands_ref_trees_false[0].tree_strata))
        self.assertEqual(1, len(self.vmi12_stands_ref_trees_false[1].tree_strata))

        # Strata with back reference to stand
        self.assertEqual(self.vmi12_stands_ref_trees_false[1], self.vmi12_stands_ref_trees_false[1].tree_strata[0].stand)
        self.assertEqual('0-999-999-98-1-01-stratum', self.vmi12_stands_ref_trees_false[1].tree_strata[0].identifier)

    def test_vmi12_stratum(self):
        stratum = self.vmi12_stands_ref_trees_false[1].tree_strata[0]
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

    def test_vmi13_init(self):
        vmi13_builder = self.vmi13_builder()
        self.assertEqual(3, len(vmi13_builder.forest_stands))
        self.assertEqual(2, len(vmi13_builder.reference_trees))
        self.assertEqual(1, len(vmi13_builder.tree_strata))

    def test_vmi13_stands(self):
        self.assertEqual(3, len(self.vmi13_stands))

    def test_vmi13_stand_identifiers(self):
        self.assertEqual('1-99-99-99-1', self.vmi13_stands[0].identifier)
        self.assertEqual('1-99-99-98-1', self.vmi13_stands[1].identifier)

    def test_vmi13_stand_variables(self):
        # test data coincides with lohkomuoto 1
        reference_area = vmi_const.vmi13_county_areas[1]
        self.assertEqual(False, self.vmi13_stands[0].auxiliary_stand)
        self.assertEqual(True, self.vmi13_stands[2].auxiliary_stand)
        self.assertEqual(reference_area, self.vmi13_stands[0].area)
        self.assertEqual(reference_area, self.vmi13_stands[1].area)
        #auxiliary stand area should be 0
        self.assertEqual(0.0, self.vmi13_stands[2].area)
        self.assertEqual(reference_area, self.vmi13_stands[0].area_weight)
        self.assertEqual(reference_area, self.vmi13_stands[1].area_weight)
        self.assertEqual(reference_area, self.vmi13_stands[2].area_weight)
        # lat 7025056.83, lon 589991.91, height 179.70
        self.assertEqual((7013044.52, 543791.23, 179.7, 'EPSG:3067'), self.vmi13_stands[0].geo_location)
        # lat 7030854.22, lon 539812.22, height 136.10
        self.assertEqual((7012044.52, 543491.23, 136.1, 'EPSG:3067'), self.vmi13_stands[1].geo_location)
        # '1019' -> 1019.0
        self.assertEqual(1019.0, self.vmi13_stands[0].degree_days)
        # '1084' -> 1084.0
        self.assertEqual(1084.0, self.vmi13_stands[1].degree_days)
        # owner group is '4' which translates to 2
        self.assertEqual(OwnerCategory.METSAHALLITUS, self.vmi13_stands[0].owner_category)
        # owner group is '1' which translated to 0
        self.assertEqual(OwnerCategory.PRIVATE, self.vmi13_stands[1].owner_category)
        self.assertEqual('1', self.vmi13_stands[0].fra_category)
        self.assertEqual('1', self.vmi13_stands[1].fra_category)
        self.assertEqual(1, self.vmi13_stands[0].land_use_category)
        self.assertEqual(1, self.vmi13_stands[1].land_use_category)
        self.assertEqual('0', self.vmi13_stands[0].land_use_category_detail)
        self.assertEqual('0', self.vmi13_stands[1].land_use_category_detail)
        # paatyyppi is '2'
        self.assertEqual(2.0, self.vmi13_stands[0].soil_peatland_category)
        # paatyyppi is '1'
        self.assertEqual(1.0, self.vmi13_stands[1].soil_peatland_category)
        # kasvupaikkatunnus is '3'
        self.assertEqual(3, self.vmi13_stands[0].site_type_category)
        # kasvupaikkatunnus is '3'
        self.assertEqual(3, self.vmi13_stands[1].site_type_category)
        # '0' -> 0
        self.assertEqual(0, self.vmi13_stands[0].tax_class_reduction)
        # '0' -> 0
        self.assertEqual(0, self.vmi13_stands[1].tax_class_reduction)
        # '2' -> 3
        self.assertEqual(3, self.vmi13_stands[0].tax_class)
        # '1' -> 2
        self.assertEqual(2, self.vmi13_stands[1].tax_class)
        # ojitus_tilanne is '3'
        self.assertEqual(DrainageCategory.TRANSFORMING_MIRE, self.vmi13_stands[0].drainage_category)
        # ojitus_tilanne is '0' and paatyyppi is '1'
        self.assertEqual(DrainageCategory.UNDRAINED_MINERAL_SOIL_OR_MIRE, self.vmi13_stands[1].drainage_category)
        # ojitus_aika is '35', year is '2020'
        self.assertEqual(1983, self.vmi13_stands[0].drainage_year)
        # ojitus_aika is '.'
        self.assertEqual(None, self.vmi13_stands[1].drainage_year)
        # value not available in VMI13 source
        self.assertEqual(None, self.vmi13_stands[0].fertilization_year)
        # value not available in VMI13 source
        self.assertEqual(None, self.vmi13_stands[1].fertilization_year)
        # ojitus_tarve is '2'
        self.assertEqual(True, self.vmi13_stands[0].drainage_feasibility)
        # ojitus_tarve is '0'
        self.assertEqual(False, self.vmi13_stands[1].drainage_feasibility)
        # '0', 2020 -> 2020
        self.assertEqual(2018, self.vmi13_stands[0].soil_surface_preparation_year)
        # '2', 2020 -> 2017
        self.assertEqual(2015, self.vmi13_stands[1].soil_surface_preparation_year)
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
        # development class '5' for 5
        self.assertEqual(5, self.vmi13_stands[0].development_class)
        # development class '3' for 3
        self.assertEqual(3, self.vmi13_stands[1].development_class)
        # viljely is '0'
        # viljely_aika is '.'
        # date is 20200522
        self.assertEqual(None, self.vmi13_stands[0].artificial_regeneration_year)
        # viljely is '1'
        # viljely_aika is 'A'
        # date is 20200503
        self.assertEqual(1998, self.vmi13_stands[1].artificial_regeneration_year)
        # hakkuu_aika is 'A', hakkuu_tapa is '0' (no operation within 10 years, A is 20 years ago)
        self.assertEqual(None, self.vmi13_stands[0].young_stand_tending_year)
        # hakkuu_aika is '6', hakkuu_tapa is '1' (no cutting, young stand tending 7 years ago)
        self.assertEqual(2011, self.vmi13_stands[1].young_stand_tending_year)
        # hakkuu_aika is 'A', hakkuu_tapa is '0' (no operation within 10 years, A is 20 years ago)
        self.assertEqual(None, self.vmi13_stands[0].cutting_year)
        # hakkuu_aika is '6', hakkuu_tapa is '1' (no cutting, young stand tending 7 years ago)
        self.assertEqual(None, self.vmi13_stands[1].cutting_year)
        # forestry_centre is 'A'
        self.assertEqual(10, self.vmi13_stands[0].forestry_centre_id)
        # forestry_centre is '9'
        self.assertEqual(9, self.vmi13_stands[1].forestry_centre_id)
        # fmc is '1'
        self.assertEqual(1, self.vmi13_stands[0].forest_management_category)
        # fmc is '1'
        self.assertEqual(1, self.vmi13_stands[1].forest_management_category)
        # hakkuu_tapa is '0' (no operation)
        self.assertEqual(None, self.vmi13_stands[0].method_of_last_cutting)
        # hakkuu_tapa is '1' (not cutting. doing young stand tending)
        self.assertEqual(None, self.vmi13_stands[1].method_of_last_cutting)
        # municipality is '12', kitukunta '176'
        self.assertEqual(12, self.vmi13_stands[0].municipality_id)
        # municipality is '11', kitukunta '402'
        self.assertEqual(11, self.vmi13_stands[1].municipality_id)
        # osuus4m is '10', osuus9m is '10'
        self.assertEqual((1.0, 1.0), self.vmi13_stands[0].area_weight_factors)
        # osuus4m is '10', osuus9m is '10'
        self.assertEqual((1.0, 1.0), self.vmi13_stands[1].area_weight_factors)
        self.assertEqual(False, self.vmi13_stands[0].auxiliary_stand)
        self.assertEqual(False, self.vmi13_stands[1].auxiliary_stand)
        self.assertEqual(26, self.vmi13_stands[0].basal_area)
        self.assertEqual(5, self.vmi13_stands[1].basal_area)

    def test_vmi13_trees(self):
        self.assertEqual(2, len(self.vmi13_stands[0].reference_trees))
        self.assertEqual(0, len(self.vmi13_stands[1].reference_trees))

        # Trees with back reference to stand
        self.assertEqual(self.vmi13_stands[0], self.vmi13_stands[0].reference_trees[0].stand)
        self.assertEqual('1-99-99-99-1-10-tree', self.vmi13_stands[0].reference_trees[0].identifier)

    def test_vmi13_tree_variables(self):
        tree = self.vmi13_stands[0].reference_trees[0]
        # '7' -> '7'
        self.assertEqual('7', tree.tree_category)
        # '1' -> 1
        self.assertEqual(TreeSpecies.PINE, tree.species)
        # '250' -> 25.0
        self.assertEqual(25.0, tree.breast_height_diameter)
        self.assertEqual(None, tree.height)
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

        #tree id source value 10
        self.assertEqual(10, tree.tree_number)

        # breast_height_age is '.' -> None
        self.assertEqual(None, tree.breast_height_age)
        # age_increase is '.', total_age is '.', breast_height_age is '.' -> None
        self.assertEqual(None, tree.biological_age)
        # living_branches_height is '.' -> 0.0
        self.assertEqual(0.0, tree.lowest_living_branch_height)
        # latvuskerros is '2' -> 1
        self.assertEqual(1, tree.management_category)
        self.assertEqual(Storey.DOMINANT, tree.storey)
        self.assertEqual('V', tree.tree_type)

    def test_vmi13_strata(self):
        self.assertEqual(0, len(self.vmi13_stands_ref_trees_false[0].tree_strata))
        self.assertEqual(1, len(self.vmi13_stands_ref_trees_false[1].tree_strata))

        # Strata with back reference to stand
        self.assertEqual(self.vmi13_stands_ref_trees_false[1], self.vmi13_stands_ref_trees_false[1].tree_strata[0].stand)
        self.assertEqual('1-99-99-98-1-1-stratum', self.vmi13_stands_ref_trees_false[1].tree_strata[0].identifier)

    def test_vmi13_stratum(self):
        stratum = self.vmi13_stands_ref_trees_false[1].tree_strata[0]
        # species is 2 -> 2
        self.assertEqual(TreeSpecies.SPRUCE, stratum.species)
        # mean_diameter is '4' (cm) -> 4.0 (cm)
        self.assertEqual(4.0, stratum.mean_diameter)
        # mean_height is '38' (dm) -> 3.8 (m)
        self.assertEqual(3.8, stratum.mean_height)
        # stems_per_ha is '1400' -> 1400.0
        self.assertEqual(1400.0, stratum.stems_per_ha)
        # breast_height_age is '7' -> 7.0
        self.assertEqual(7.0, stratum.breast_height_age)
        # origin is '3' -> 2
        self.assertEqual(2, stratum.origin)
        # biological_age is '8' -> 15.0; (biological_age + breast_height_age = 15.0)
        self.assertEqual(15.0, stratum.biological_age)
        # basal area is '2' -> 2.0
        self.assertEqual(2.0, stratum.basal_area)
        self.assertEqual(Storey.DOMINANT, stratum.storey)


    def test_remove_strata(self):
        stands = deepcopy(self.vmi13_stands)
        self.vmi13_builder().remove_strata(stands)
        self.assertEqual(0, len(stands[1].tree_strata))

