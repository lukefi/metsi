import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
import forestry.r_utils


class RUtilsTest(unittest.TestCase):
    def test_lmfor_volume(self):
        fixture = ForestStand(degree_days=720.3)
        fixture.reference_trees = [
            ReferenceTree(height=10.4, breast_height_diameter=20.3, species=1),
            ReferenceTree(height=13.4, breast_height_diameter=14.3, species=2)
        ]

        result = forestry.r_utils.lmfor_volume(fixture)
        self.assertEqual(170.0, result)
