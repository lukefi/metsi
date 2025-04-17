import unittest
from lukefi.metsi.forestry.preprocessing.coordinate_conversion import \
    CRS, convert_location_to_ykj, _erts_tm35_to_ykj
from lukefi.metsi.data.model import ForestStand

class TestCoordinateConversion(unittest.TestCase):
    def test_coordinate_conversion(self):
        u = 6640610.26
        v = 267924.92
        (x, y) = _erts_tm35_to_ykj(u, v)
        self.assertEqual(x, 6643400.000631507)
        self.assertEqual(y, 3268000.003019635)

    def test_convert_location_to_ykj(self):
        dummy_float = 0.0
        target_crs = 'EPSG:2393'
        # Already in target CRS
        passthrough_gl = tuple((dummy_float for _ in range(3))) + ('EPSG:2393',)
        stand_assertion = ForestStand(geo_location=passthrough_gl)
        result = convert_location_to_ykj(stand_assertion)
        self.assertEqual(result[0], dummy_float)
        self.assertEqual(result[1], dummy_float)
        self.assertEqual(result[3], target_crs)
        # Valid for YKJ-conversion
        valid_gl = (6640610.26, 267924.92, dummy_float, 'EPSG:3067')
        stand_assertion.geo_location=valid_gl
        result = convert_location_to_ykj(stand_assertion)
        self.assertEqual(result[0], 6643400.000631507)
        self.assertEqual(result[1], 3268000.003019635)
        self.assertEqual(result[3], target_crs)
        # Invalid CRS raises exception
        invalid_gl = tuple((dummy_float for _ in range(3))) + ('InvalidCRS',)
        invalid_stand = ForestStand(geo_location=invalid_gl)
        self.assertRaises(Exception,
            convert_location_to_ykj(invalid_stand))
