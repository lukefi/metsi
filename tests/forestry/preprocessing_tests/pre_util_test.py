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
