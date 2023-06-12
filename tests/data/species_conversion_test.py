from lukefi.metsi.data.enums.internal import TreeSpecies
from tests.data import test_util
from lukefi.metsi.data.conversion import vmi2internal, fc2internal


class TestConversion(test_util.ConverterTestSuite):
    def test_convert_VMI_species_to_internal_species(self):
        assertions = [
            (["A9"], TreeSpecies.YEW),
            (["A1"], TreeSpecies.SHORE_PINE),
            (["0"], TreeSpecies.UNKNOWN),
        ]
        self.run_with_test_assertions(
            assertions, vmi2internal.convert_species)

    def test_convert_FC_species_to_internal_species(self):
        assertions = [
            (["1"], TreeSpecies.PINE),
            (["29"], TreeSpecies.UNKNOWN_DECIDUOUS),
        ]
        self.run_with_test_assertions(
            assertions, fc2internal.convert_species)
