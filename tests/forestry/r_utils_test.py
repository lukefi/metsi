import unittest

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
try:
    unrunnable = False
    import lukefi.metsi.forestry.r_utils as r_utils
except ImportError:
    unrunnable = True


@unittest.skipIf(unrunnable, "rpy2 not installed")
class RUtilsTest(unittest.TestCase):
    def test_lmfor_volume(self):
        fixture = ForestStand(degree_days=720.3)
        fixture.reference_trees_pre_vec = [
            ReferenceTree(height=10.4, breast_height_diameter=20.3, species=TreeSpecies.PINE),
            ReferenceTree(height=13.4, breast_height_diameter=14.3, species=TreeSpecies.SILVER_BIRCH)
        ]

        result = r_utils.lmfor_volume(fixture)
        self.assertAlmostEqual(147.55, result, 0)
