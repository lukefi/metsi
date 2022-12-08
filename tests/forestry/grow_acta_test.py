import unittest

from forestry.grow_acta import grow_acta
from tests.test_utils import prepare_growth_test_stand


class GrowActaTest(unittest.TestCase):
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
        #self.assertEqual(stand.reference_trees[0].biological_age, 60)
        #self.assertEqual(stand.reference_trees[1].biological_age, 42)
        #self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        #self.assertEqual(stand.reference_trees[2].breast_height_age, 0)
        self.assertEqual(stand.year, 2030)
