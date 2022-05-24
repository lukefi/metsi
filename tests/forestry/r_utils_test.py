import unittest
from forestry.ForestDataModels import ForestStand, ReferenceTree
import forestry.r_utils


class RUtilsTest(unittest.TestCase):
    def test_lmfor_volume(self):
        fixture = ForestStand()
        fixture.reference_trees = [
            ReferenceTree(),
            ReferenceTree()
        ]
        fixture.reference_trees[0].height = 10.4
        fixture.reference_trees[0].breast_height_diameter = 20.3
        fixture.reference_trees[0].species = 1
        fixture.reference_trees[1].height = 13.4
        fixture.reference_trees[1].breast_height_diameter = 14.3
        fixture.reference_trees[1].species = 2
        fixture.degree_days = 720.3

        result = forestry.r_utils.lmfor_volume(fixture)
        self.assertEqual(173.8, result)
