import unittest

from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand, ReferenceTree

from forestry.grow_motti import grow_motti
from forestry.preprocessing import compute_location_metadata
from tests.test_utils import prepare_growth_test_stand


class GrowMottiTest(unittest.TestCase):
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
