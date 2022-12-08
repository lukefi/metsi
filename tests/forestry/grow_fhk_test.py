from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand, ReferenceTree
import unittest

from tests.test_utils import prepare_growth_test_stand

try:
    import fhk
    from forestry.grow_fhk import grow_fhk
except ImportError:
    fhk = None

@unittest.skipIf(fhk is None, "fhk not installed")
class GrowFhkTest(unittest.TestCase):
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
