import unittest

from forestry.grow_acta import grow_acta
from forestry.grow_motti import grow_motti
from tests.test_utils import prepare_growth_test_stand

try:
    import fhk
    from forestry.grow_fhk import grow_fhk
except ImportError:
    fhk = None


class GrowthOperationsTest(unittest.TestCase):

    @unittest.skipIf(fhk is None, "fhk not installed")
    def test_grow_fhk(self):
        stand = prepare_growth_test_stand()
        grow_fhk(
            (stand, None),
            graph="tests/resources/graph.g.lua",
            luapath="tests/resources/?.lua"
        )
        self.assertAlmostEqual(stand.reference_trees[0].stems_per_ha, 100, 2)
        self.assertAlmostEqual(stand.reference_trees[1].stems_per_ha, 100, 2)
        self.assertAlmostEqual(stand.reference_trees[2].stems_per_ha, 100, 2)
        self.assertAlmostEqual(stand.reference_trees[0].breast_height_diameter, 31.46, 2)
        self.assertAlmostEqual(stand.reference_trees[1].breast_height_diameter, 27.91, 2)
        self.assertAlmostEqual(stand.reference_trees[2].breast_height_diameter, 1.46, 2)
        self.assertAlmostEqual(stand.reference_trees[0].height, 20.73, 2)
        self.assertAlmostEqual(stand.reference_trees[1].height, 18.46, 2)
        self.assertAlmostEqual(stand.reference_trees[2].height, 1.03, 2)
        self.assertTrue(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[0].biological_age, 60)
        self.assertEqual(stand.reference_trees[1].biological_age, 42)
        self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 0)
        self.assertEqual(stand.year, 2030)

        # grow again to trigger tree 3 to grow from sapling to mature
        grow_fhk(
            (stand, None),
            graph="tests/resources/graph.g.lua",
            luapath="tests/resources/?.lua"
        )

        self.assertAlmostEqual(stand.reference_trees[2].stems_per_ha, 100, 2)
        self.assertAlmostEqual(stand.reference_trees[2].breast_height_diameter, 2.91, 2)
        self.assertAlmostEqual(stand.reference_trees[2].height, 1.76, 2)
        self.assertFalse(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[2].biological_age, 11)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 11)

    def test_grow_motti(self):
        stand = prepare_growth_test_stand()
        grow_motti((stand, None))
        self.assertEqual(len(stand.reference_trees), 3)
        self.assertAlmostEqual(122.83, stand.reference_trees[0].stems_per_ha, 2)
        self.assertAlmostEqual(stand.reference_trees[1].stems_per_ha, 122.33, 2)
        self.assertAlmostEqual(stand.reference_trees[2].stems_per_ha, 90.69, 2)
        self.assertAlmostEqual(stand.reference_trees[0].breast_height_diameter, 31.86, 2)
        self.assertAlmostEqual(stand.reference_trees[1].breast_height_diameter, 28.40, 2)
        self.assertAlmostEqual(stand.reference_trees[2].breast_height_diameter, 1.67, 2)
        self.assertAlmostEqual(stand.reference_trees[0].height, 21.48, 2)
        self.assertAlmostEqual(stand.reference_trees[1].height, 18.81, 2)
        self.assertAlmostEqual(stand.reference_trees[2].height, 2.91, 2)
        self.assertFalse(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[0].biological_age, 60)
        self.assertEqual(stand.reference_trees[1].biological_age, 42)
        self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 6)
        self.assertEqual(stand.year, 2030)

    def test_grow_acta(self):
        stand = prepare_growth_test_stand()
        grow_acta((stand, None))

        self.assertEqual(len(stand.reference_trees), 3)
        self.assertAlmostEqual(stand.reference_trees[0].stems_per_ha, 123, 2)
        self.assertAlmostEqual(stand.reference_trees[1].stems_per_ha, 123, 2)
        self.assertAlmostEqual(stand.reference_trees[2].stems_per_ha, 123, 2)
        self.assertAlmostEqual(stand.reference_trees[0].breast_height_diameter, 31.96, 2)
        self.assertAlmostEqual(stand.reference_trees[1].breast_height_diameter, 28.61, 2)
        self.assertAlmostEqual(stand.reference_trees[2].breast_height_diameter, 0, 2)
        self.assertAlmostEqual(stand.reference_trees[0].height, 21.42, 2)
        self.assertAlmostEqual(stand.reference_trees[1].height, 18.87, 2)
        self.assertAlmostEqual(stand.reference_trees[2].height, 0.6, 2)
        self.assertTrue(stand.reference_trees[2].sapling)
        # grow_acta doesn't increase ages at this moment. needs FFL change
        # self.assertEqual(stand.reference_trees[0].biological_age, 60)
        # self.assertEqual(stand.reference_trees[1].biological_age, 42)
        # self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        # self.assertEqual(stand.reference_trees[2].breast_height_age, 0)
        self.assertEqual(stand.year, 2030)
