""" Tests suites for forestryfunctions.preprocessing.* modules """
import unittest
from lukefi.metsi.data.model import TreeStratum
from lukefi.metsi.forestry.preprocessing import pre_util


class TestPreprocessingUtils(unittest.TestCase):

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
