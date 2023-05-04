"""
NOTE: this test suite has been intentionally duplicated from `forestry-function-library` and the implementation here should follow the source. 
"""
from lukefi.metsi.data.enums.internal import TreeSpecies

from lukefi.metsi.data.formats import vmi_supplementing
from tests.data import test_util


class TestNaslund(test_util.ConverterTestSuite):
    def test_naslund_height(self):
        assertions = [
            ([0.0, TreeSpecies.PINE], None),  # diameter must be > 0
            ([10.0, TreeSpecies.PINE], 14.58),
            ([10.0, TreeSpecies.DOUGLAS_FIR], 14.58), #other coniferous species
            ([20.0, TreeSpecies.JUNIPER], 20.25), #other coniferous species
            ([10.0, TreeSpecies.SPRUCE], 9.85),
            ([20.0, TreeSpecies.SPRUCE], 17.1),
            ([10.0, TreeSpecies.SILVER_BIRCH], 10.38),
            ([20.0, TreeSpecies.SILVER_BIRCH], 13.45),
            ([10.0, TreeSpecies.UNKNOWN], 10.38),
        ]
        self.run_with_test_assertions(assertions, vmi_supplementing.naslund_height)
