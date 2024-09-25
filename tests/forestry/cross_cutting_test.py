import unittest
import numpy as np
from lukefi.metsi.data.enums.internal import TreeSpecies
from parameterized import parameterized
from lukefi.metsi.forestry.cross_cutting.cross_cutting import ZERO_DIAMETER_DEFAULTS, cross_cut, _cross_cut_species_mapper
from tests.forestry.test_util import DEFAULT_TIMBER_PRICE_TABLE, TestCaseExtension

unrunnable = False
try:
    import rpy2.robjects as robjects
    import lukefi.metsi.forestry.r_utils as r_utils
except ImportError:
    unrunnable = True


@unittest.skipIf(unrunnable, "rpy2 not installed")
class CrossCuttingTest(TestCaseExtension):
    def _cross_cut_with_r(
        self,
        species: TreeSpecies,
        breast_height_diameter: float,
        height: float,
        timber_price_table,
        div = 10
        ) -> tuple[dict, dict]:
        """This function is used only to to test the python-ported version of the cross-cutting scripts against the original R version."""

        species_string = _cross_cut_species_mapper.get(species, "birch") #birch is used as the default species in cross §cutting
        height = round(height)

        r = robjects.r
        r.source("./tests/forestry/resources/cross_cutting/cross_cutting_main.R")
        result = r["cross_cut"](species_string, breast_height_diameter, height)
        result = r_utils.convert_r_named_list_to_py_dict(result)
        return (result["volumes"], result["values"])

    @parameterized.expand([
        (TreeSpecies.PINE,30,25),
        (TreeSpecies.UNKNOWN_CONIFEROUS, 15.57254199723247, 18.293846547993535),
        (TreeSpecies.SPRUCE, 17.721245087039236, 16.353742669109522)
    ])
    def test_implementation_equality(self, species, breast_height_diameter, height):
        P = DEFAULT_TIMBER_PRICE_TABLE
        _, vol_lupa, val_lupa = cross_cut(species, breast_height_diameter, height, P, 10, "lupa")
        _, vol_py, val_py = cross_cut(species, breast_height_diameter, height, P, 10, "py")
        vol_r, val_r = self._cross_cut_with_r(species, breast_height_diameter, height, DEFAULT_TIMBER_PRICE_TABLE)
        self.assertTrue(np.allclose(vol_lupa, np.array(vol_r), atol=10e-6))
        self.assertTrue(np.allclose(vol_py, np.array(vol_r), atol=10e-6))
        self.assertTrue(np.allclose(val_lupa, np.array(val_r), atol=10e-6))
        self.assertTrue(np.allclose(val_py, np.array(val_r), atol=10e-6))

    def test_cross_cut_zero_dbh_tree_returns_constant_values(self):
        for dbh in [0, None]:
            unique_timber_grades, volumes, values = cross_cut(TreeSpecies.PINE, dbh, 10, DEFAULT_TIMBER_PRICE_TABLE)
            self.assertTrue(len(unique_timber_grades) == len(volumes) == len(values) == 1)
            self.assertEqual(unique_timber_grades[0], ZERO_DIAMETER_DEFAULTS[0][0])
            self.assertEqual(volumes[0], ZERO_DIAMETER_DEFAULTS[1][0])
            self.assertEqual(values[0], ZERO_DIAMETER_DEFAULTS[2][0])
        self.assertRaises(ValueError, cross_cut, *(TreeSpecies.PINE, -1, 10, DEFAULT_TIMBER_PRICE_TABLE))
