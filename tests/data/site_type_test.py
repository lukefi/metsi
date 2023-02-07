from parameterized import parameterized
import unittest
from lukefi.metsi.data.enums.internal import SiteType
from lukefi.metsi.data.conversion import vmi2internal, fc2internal


class TestConversion(unittest.TestCase):

    @parameterized.expand(
        [
            ('1', SiteType.VERY_RICH_SITE),
            ('2', SiteType.RICH_SITE),
            ('T', SiteType.TUNTURIKOIVIKKO),
            ('A', SiteType.OPEN_MOUNTAINS),
        ]
    )
    def test_convert_VMI_site_type_to_internal(self, code, expected):
        result = vmi2internal.convert_site_type_category(code)
        self.assertEqual(result, expected)


    @parameterized.expand(
        [
            ('1', SiteType.VERY_RICH_SITE),
            ('2', SiteType.RICH_SITE),
            ('7', SiteType.ROCKY_OR_SANDY_AREA),
            ('8', SiteType.OPEN_MOUNTAINS),
        ]
    )
    def test_convert_FFC_site_type_to_internal(self, code, expected):
        result = fc2internal.convert_site_type_category(code)
        self.assertEqual(result, expected)