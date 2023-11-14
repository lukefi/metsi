import unittest
from parameterized import parameterized
from lukefi.metsi.data.enums.internal import DrainageCategory
from lukefi.metsi.data.conversion import vmi2internal, fc2internal


class TestConversion(unittest.TestCase):

    @parameterized.expand([
        ("0", DrainageCategory.UNDRAINED_MINERAL_SOIL_OR_MIRE),
        ("1", DrainageCategory.DITCHED_MINERAL_SOIL)
    ])
    def test_convert_VMI_drainage_category_to_internal(self, code, expected):
        result = vmi2internal.convert_drainage_category(code)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ("1", DrainageCategory.UNDRAINED_MINERAL_SOIL),
        ("6", DrainageCategory.UNDRAINED_MIRE)
    ])
    def test_convert_FC_drainage_category_to_internal(self, code, expected):
        result = fc2internal.convert_drainage_category(code)
        self.assertEqual(result, expected)
    
    @parameterized.expand([
        ("1", fc2internal.convert_drainage_category, DrainageCategory.UNDRAINED_MINERAL_SOIL),
        (None, lambda a: a, None),
    ])
    def test_general_FC_conversion(self, code, f, expected):
        result = fc2internal.convert_to_internal(code, f)
        self.assertEqual(result, expected)