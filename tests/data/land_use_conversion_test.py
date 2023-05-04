from lukefi.metsi.data.enums.internal import LandUseCategory
from tests.data import test_util
from lukefi.metsi.data.conversion import vmi2internal, fc2internal


class TestConversion(test_util.ConverterTestSuite):
    def test_convert_VMI_lu_category_to_internal(self):
        assertions = [
            (["1"], LandUseCategory.FOREST),
            (["A"], LandUseCategory.FRESHWATER),
        ]

        self.run_with_test_assertions(
            assertions, vmi2internal.convert_land_use_category)

        #convertsion should raise exception for an unexpected value "foo"
        self.assertRaises(ValueError, vmi2internal.convert_land_use_category, *["foo"])
        
        #conversion should fail if a true code is passed in lowercase (responsibility of caller to pass in uppercase)
        self.assertRaises(ValueError, vmi2internal.convert_land_use_category, *["a"])


    def test_convert_FC_lu_category_to_internal(self):
        assertions = [
            (["1"], LandUseCategory.FOREST),
            (["2"], LandUseCategory.SCRUB_LAND),
            (["3"], LandUseCategory.WASTE_LAND),
        ]

        self.run_with_test_assertions(
            assertions, fc2internal.convert_land_use_category)

        #convertsion should raise exception for an unexpected value "foo"
        self.assertRaises(ValueError, fc2internal.convert_land_use_category, *["foo"])
