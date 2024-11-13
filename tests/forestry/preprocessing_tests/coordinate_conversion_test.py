import unittest
from lukefi.metsi.forestry.preprocessing.coordinate_conversion import erts_tm35_to_ykj


class TestCoordinateConversion(unittest.TestCase):
    def test_coordinate_conversion(self):
        u = 6640610.26
        v = 267924.92
        (x, y) = erts_tm35_to_ykj(u, v)
        self.assertEqual(x, 6643400.000631507)
        self.assertEqual(y, 3268000.003019635)