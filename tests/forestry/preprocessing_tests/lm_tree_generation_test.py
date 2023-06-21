import unittest
from statistics import mean

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from lukefi.metsi.forestry.preprocessing.tree_generation_lm import tree_generation_lm


class TestLmTreeGeneration(unittest.TestCase):
    def test_lm_tree_generation(self):
        G = 70.0
        DDY = 952.0
        stratum = TreeStratum(
            mean_diameter=28.0,
            basal_area=34.0,
            mean_height=22.0,
            species=TreeSpecies.PINE
        )
        trees = [
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=26.0,
                height=19.0,
                measured_height=17.9
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=24.0,
                height=17.0,
                measured_height=None
            )
        ]
        stratum._trees = trees
        result = tree_generation_lm(stratum, DDY, G)
        self.assertEqual(10, len(result))
        self.assertAlmostEqual(stratum.mean_height, mean([t.height for t in result]), delta=6)
        self.assertAlmostEqual(stratum.mean_diameter, mean([t.breast_height_diameter for t in result]), delta=7)
