from tests.data import test_util
from lukefi.metsi.data.conversion import vmi2internal, fc2internal
from lukefi.metsi.data.enums.internal import OwnerCategory

class TestConversion(test_util.ConverterTestSuite):
    def test_convert_VMI_owner_to_internal(self):
        assertions = [
            (["1"], OwnerCategory.PRIVATE),
            (["2"], OwnerCategory.FOREST_INDUSTRY),
            (["A"], OwnerCategory.UNDIVIDED)
        ]

        self.run_with_test_assertions(
            assertions, vmi2internal.convert_owner
        )

    def test_convert_FFC_owner_to_internal(self):
        assertions = [
            (["1"], OwnerCategory.PRIVATE),
            (["2"], OwnerCategory.FOREST_INDUSTRY),
            (["4"], OwnerCategory.OTHER_COMMUNITY)
        ]

        self.run_with_test_assertions(
            assertions, fc2internal.convert_owner
        )
