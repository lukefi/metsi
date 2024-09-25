import unittest

from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.data.enums import internal


class TestForestDataModel(unittest.TestCase):

    def test_stratum_to_sapling_reference_tree(self):
        assertion = ReferenceTree(
            stems_per_ha = 1200,
            species = internal.TreeSpecies(1),
            breast_height_diameter = 1.0,
            height = 2.0,
            breast_height_age = 10.0,
            biological_age = 12.0,
            saw_log_volume_reduction_factor = -1.0,
            pruning_year = 0,
            age_when_10cm_diameter_at_breast_height = 0,
            origin = 1,
            stand_origin_relative_position = (0.0, 0.0, 0.0),
            management_category = 1,
            sapling = True)
        fixture = TreeStratum(
            sapling_stems_per_ha = 1200,
            species = internal.TreeSpecies.PINE,
            mean_diameter = 1.0,
            mean_height = 2.0,
            breast_height_age = 10.0,
            biological_age = 12.0,
            origin = 1)
        self.assertEqual(fixture.to_sapling_reference_tree().identifier, assertion.identifier)

    def test_stratum_has_sapling_stems_per_ha(self):
        fixture = TreeStratum()
        assertions = [
            (10.0, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.sapling_stems_per_ha = i[0]
            self.assertEqual(i[1], fixture.has_sapling_stems_per_ha())

    def test_stratum_has_height(self):
        fixture = TreeStratum()
        assertions = [
            (10.0, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.mean_height = i[0]
            self.assertEqual(i[1], fixture.has_height())

    def test_stratum_get_breast_height_age(self):
        fixture = TreeStratum()
        assertions = [
            ((10.0, 10.0), 10.0),
            ((10.0, None), 10),
            ((None, 10.0), 0.0),
            ((None, 20.0), 8.0),
            ((None, None), 0.0),
        ]
        for i in assertions:
            fixture.breast_height_age = i[0][0]
            fixture.biological_age = i[0][1]
            self.assertEqual(i[1], fixture.get_breast_height_age())
        # Final test case for different default param.
        fixture.breast_height_age = None
        fixture.biological_age = 20.0
        self.assertEqual(10.0, fixture.get_breast_height_age(subtrahend=10))

    def test_has_stems_per_ha(self):
        fixture = TreeStratum()
        assertions = [
            (10.0, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.stems_per_ha = i[0]
            self.assertEqual(i[1], fixture.has_stems_per_ha())


    def test_stratum_has_basal_area(self):
        fixture = TreeStratum()
        assertions = [
            (10.0, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.basal_area = i[0]
            self.assertEqual(i[1], fixture.has_basal_area())

    def test_stratum_has_breast_height_age(self):
        fixture = TreeStratum()
        assertions = [
            (10.0, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.breast_height_age = i[0]
            self.assertEqual(i[1], fixture.has_breast_height_age())


    def test_reference_tree_has_biological_age(self):
        fixture = ReferenceTree()
        assertions = [
            (10.0, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.biological_age = i[0]
            self.assertEqual(i[1], fixture.has_biological_age())

    def test_reference_tree_has_diameter(self):
        fixture = ReferenceTree()
        assertions = [
            (11.5, True),
            (None, False),
            (-10.0, False),
            (0.0, False),
        ]
        for i in assertions:
            fixture.breast_height_diameter = i[0]
            self.assertEqual(i[1], fixture.has_diameter())

    def test_set_area_without_weight(self):
        fixture = ForestStand()
        fixture.set_area(1.0)
        self.assertEqual(1.0, fixture.area)
        self.assertEqual(1.0, fixture.area_weight)

    def test_set_area_with_weight(self):
        fixture = ForestStand()
        fixture.set_area(1.0)
        self.assertEqual(1.0, fixture.area)
        self.assertEqual(1.0, fixture.area_weight)

    def test_set_geo_location(self):
        fixture = ForestStand()
        assertions = [
            ((6000.1, 304.3, 10.0), (6000.1, 304.3, 10.0, 'EPSG:3067')),
            ((6000.1, 304.3, None), (6000.1, 304.3, None, 'EPSG:3067'))
        ]
        failures = [
            (None, 20.3, 20),
            (23.4, None, 20),

        ]
        for i in assertions:
            fixture.set_geo_location(*i[0])
            self.assertEqual(i[1], fixture.geo_location)
        for i in failures:
            self.assertRaises(Exception, lambda: fixture.set_geo_location(*i))

    def test_convert_csv_stand_row_with_missing_altitude(self):
        row = "stand;12345;1;2018;436.0;436.0;6834156.23;429291.91;None;EPSG:3067;1019.0;" \
              "4;1;2;" \
              "3;0;3;8;True;1984;None;2018;False;None;0;None;None;" \
              "None;None;10;1;None;12;1;0;False;1.0;1.0;1;10;51"
        row = row.split(';')
        stand = ForestStand.from_csv_row(row)

        self.assertEqual((6834156.23, 429291.91, None, 'EPSG:3067'), stand.geo_location)
