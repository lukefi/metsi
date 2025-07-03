import csv
import unittest
from io import StringIO
from lukefi.metsi.data.formats.io_utils import *
from tests.data.test_util import ConverterTestSuite, ForestBuilderTestBench
from lukefi.metsi.data.formats.io_utils import c_var_rst_row
from lukefi.metsi.data.model import ForestStand

vmi13_builder = ForestBuilderTestBench.vmi13_builder()


class TestCVarRstRow(unittest.TestCase):

    def setUp(self):
        # Mock ForestStand object
        self.mock_stand = ForestStand(
            identifier="123",
            stand_id=1,
            reference_trees=[],
            tree_strata=[]
        )
        self.mock_stand.get_value_list = lambda cvar_decl: [1.23, 4.56, 7.89]  # Mock method

    def test_c_var_rst_row(self):
        cvar_decl = ["var1", "var2", "var3"]
        result = c_var_rst_row(self.mock_stand, cvar_decl)
        expected = "123.000000 5.000000 2.000000 3.000000 1.230000 4.560000 7.890000"
        self.assertEqual(result, expected)


class IoUtilsTest(ConverterTestSuite):
    def test_rst_float(self):
        assertions = [
            ([123], "123.000000"),
            ([0], "0.000000"),
            ([123.4455667788], "123.445567"),
            ([None], "0.000000"),
            (["1.23"], "1.230000"),
            (["abc"], "0.000000")
        ]
        self.run_with_test_assertions(assertions, rst_float)

    def test_rst_forest_stand_rows(self):
        vmi13_stands = vmi13_builder.build()
        result = rst_forest_stand_rows(vmi13_stands[1], additional_vars=[])
        self.assertEqual(4, len(result))

    def test_rsts_forest_stand_rows(self):
        vmi13_stands = vmi13_builder.build()
        result = rsts_forest_stand_rows(vmi13_stands[1])
        self.assertEqual(3, len(result))

    def test_rst_rows(self):
        vmi13_stands = vmi13_builder.build()
        container = ExportableContainer(vmi13_stands, additional_vars=None)
        result = stands_to_rst_content(container)
        self.assertEqual(10, len(result))

    def test_rsts_rows(self):
        vmi13_stands = vmi13_builder.build()
        container = ExportableContainer(vmi13_stands, additional_vars=None)
        result = stands_to_rsts_content(container)
        self.assertEqual(7, len(result))

    def test_stands_to_csv(self):
        delimiter = ";"
        vmi13_stands = vmi13_builder.build()
        container = ExportableContainer(vmi13_stands, additional_vars=None)
        result = stands_to_csv_content(container, delimiter)
        self.assertEqual(13, len(result))
        
        #make sure that each type of a row has the same number of columns, since csv-->stand conversion relies on it
        stand_row_lengths = [len(row.split(delimiter)) for row in result if row[0:5] == "stand"]
        tree_row_lengths = [len(row.split(delimiter)) for row in result if row[0:4] == "tree"]
        stratum_rows_lengths = [len(row.split(delimiter)) for row in result if row[0:7] == "stratum"]

        self.assertTrue(all(length==stand_row_lengths[0] for length in stand_row_lengths))
        self.assertTrue(all(length==tree_row_lengths[0] for length in tree_row_lengths))
        self.assertTrue(all(length==stratum_rows_lengths[0] for length in stratum_rows_lengths))

    def test_csv_to_stands(self):
        """tests that the roundtrip conversion stands-->csv-->stands maintains the stand structure"""
        vmi13_stands = vmi13_builder.build()
        delimiter = ";"
        serialized = '\n'.join(stands_to_csv_content(ExportableContainer(vmi13_stands, None), delimiter))
        deserialized = list(csv.reader(StringIO(serialized), delimiter=delimiter))
        stands_from_csv = csv_content_to_stands(deserialized)
        self.assertEqual(4, len(stands_from_csv))

        # Test that the stands from csv and the original stands are equal.
        # Perform comparison of dicts for each relevant object, setting relations to None to avoid recursive loop
        for i in range(len(vmi13_stands)):
            for t in range(len(vmi13_stands[i].reference_trees)):
                trees_expected = vmi13_stands[i].reference_trees[t].__dict__
                trees_actual = stands_from_csv[i].reference_trees[t].__dict__
                trees_expected['stand'] = None
                trees_actual['stand'] = None
                self.assertTrue(trees_expected == trees_actual)
            
            for s in range(len(vmi13_stands[i].tree_strata)):
                strata_expected = vmi13_stands[i].tree_strata[s].__dict__
                strata_actual = stands_from_csv[i].tree_strata[s].__dict__
                strata_expected['stand'] = None
                strata_actual['stand'] = None
                self.assertTrue(strata_expected == strata_actual)

            stands_expected = vmi13_stands[i].__dict__
            stands_actual = stands_from_csv[i].__dict__
            stands_expected['reference_trees'] = None
            stands_expected['tree_strata'] = None
            stands_actual['reference_trees'] = None
            stands_actual['tree_strata'] = None
            stands_expected['reference_trees_soa'] = None
            stands_expected['tree_strata_soa'] = None
            stands_actual['reference_trees_soa'] = None
            stands_actual['tree_strata_soa'] = None
            self.assertTrue(stands_expected == stands_actual)

