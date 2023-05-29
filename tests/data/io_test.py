import csv
from io import StringIO
from lukefi.metsi.data.formats.io_utils import *
from tests.data.test_util import ConverterTestSuite, vmi13_builder


class IoUtilsTest(ConverterTestSuite):
    def test_rsd_float(self):
        assertions = [
            ([123], "123.000000"),
            ([0], "0.000000"),
            ([123.4455667788], "123.445567"),
            ([None], "0.000000"),
            (["1.23"], "1.230000"),
            (["abc"], "0.000000")
        ]
        self.run_with_test_assertions(assertions, rsd_float)

    def test_rsd_forest_stand_rows(self):
        vmi13_stands = vmi13_builder.build()
        result = rsd_forest_stand_rows(vmi13_stands[0])
        self.assertEqual(3, len(result))

    def test_rsd_rows(self):
        vmi13_stands = vmi13_builder.build()
        result = stands_to_rsd_content(vmi13_stands)
        self.assertEqual(5, len(result))

    def test_stands_to_csv(self):
        delimiter = ";"
        vmi13_stands = vmi13_builder.build()
        result = stands_to_csv_content(vmi13_stands, delimiter)
        self.assertEqual(6, len(result))
        
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
        serialized = '\n'.join(stands_to_csv_content(vmi13_stands, delimiter))
        deserialized = list(csv.reader(StringIO(serialized), delimiter=delimiter))
        stands_from_csv = csv_content_to_stands(deserialized)
        self.assertEqual(2, len(stands_from_csv))

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
            self.assertTrue(stands_expected == stands_actual)

