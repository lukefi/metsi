""" Tests suites for forestryfunctions.preprocessing.* modules """
import unittest
from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from lukefi.metsi.forestry.preprocessing import pre_util


class TestPreprocessingUtils(unittest.TestCase):
    def test_stratum_needs_diameter(self):
        assertions = [
            [(10.0, None), True],
            [(10.0, 0.0), True],
            [(0.0, 0.0), False],
            [(0.0, 1.0), False],
            [(0.0, 10.0), False],
            [(None, 10.0), False]
        ]
        for i in assertions:
            stratum = TreeStratum()
            stratum.mean_height = i[0][0]
            stratum.mean_diameter = i[0][1]
            result = pre_util.stratum_needs_diameter(stratum)
            self.assertEqual(i[1], result)

    def test_supplement_mean_diameter(self):
        assertions = [
            [(10.0, None), 12.0],
            [(10.0, 0.0), 12.0],
            [(10.0, 0.0), 12.0]
        ]
        for i in assertions:
            stratum = TreeStratum()
            stratum.mean_height = i[0][0]
            stratum.mean_diameter = i[0][1]
            result = pre_util.supplement_mean_diameter(stratum)
            self.assertEqual(i[1], result.mean_diameter)

    def test_stems_scaling(self):
        factors = (2.0, 4.0)
        reftree1 = ReferenceTree()
        reftree1.stems_per_ha = 10
        reftree1.breast_height_diameter = 0.5
        reftree2 = ReferenceTree()
        reftree2.stems_per_ha = 10
        reftree2.breast_height_diameter = 1
        scaled = pre_util.scale_stems_per_ha([reftree1, reftree2], factors)

        self.assertEqual(20.0, scaled[0].stems_per_ha)
        self.assertEqual(40.0, scaled[1].stems_per_ha)
