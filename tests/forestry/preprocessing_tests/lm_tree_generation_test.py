import unittest
from statistics import mean

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from lukefi.metsi.forestry.preprocessing.tree_generation_lm import tree_generation_lm


class TestLmTreeGeneration(unittest.TestCase):
    def test_lm_tree_generation(self):
        G = 17.0
        DDY = 1271.0
        stratum = TreeStratum(
            mean_diameter=17.0,
            basal_area=17.0,
            mean_height=14.5,
            species=TreeSpecies.PINE,
            stems_per_ha=0.0
        )
        trees = [
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=7.5,
                height=7.0,
                measured_height= None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=9.0,
                height=7.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=21.5,
                height=17.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=17.1,
                height=13.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=17.8,
                height=13.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=15.4,
                height=13.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=14.5,
                height=7.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=26.7,
                height=17.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=24.4,
                height=13.0,
                measured_height=13.4,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=20.1,
                height=13.0,
                measured_height=10.0,
                tuhon_ilmiasu = '0'
            ),
            ReferenceTree(
                species=TreeSpecies.PINE,
                breast_height_diameter=17.0,
                height=13.0,
                measured_height=None,
                tuhon_ilmiasu = '0'
            ),
        ]
        stratum._trees = trees
        result = tree_generation_lm(stratum, DDY, G)
        self.assertEqual(7, len(result))
        self.assertAlmostEqual(stratum.mean_height, mean([t.height for t in result]), delta=4)
        self.assertAlmostEqual(stratum.mean_diameter, mean([t.breast_height_diameter for t in result]), delta=4)
