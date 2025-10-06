import csv
import unittest
from io import StringIO

import numpy as np
from lukefi.metsi.data.formats.io_utils import *
from lukefi.metsi.data.vector_model import ReferenceTrees, TreeStrata
from lukefi.metsi.data.vectorize import vectorize
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
            reference_trees_pre_vec=[],
            tree_strata_pre_vec=[]
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
        vectorize(vmi13_stands)
        result = rst_forest_stand_rows(vmi13_stands[1], additional_vars=[])
        self.assertEqual(4, len(result))

    def test_rst_rows(self):
        vmi13_stands = vmi13_builder.build()
        vectorize(vmi13_stands)
        container = ExportableContainer(vmi13_stands, additional_vars=None)
        result = stands_to_rst_content(container)
        self.assertEqual(10, len(result))

    def test_stands_to_csv(self):
        delimiter = ";"
        vmi13_stands = vmi13_builder.build()
        vectorize(vmi13_stands)
        container = ExportableContainer(vmi13_stands, additional_vars=None)
        result = stands_to_csv_content(container, delimiter)
        self.assertEqual(13, len(result))

        # make sure that each type of a row has the same number of columns, since csv-->stand conversion relies on it
        stand_row_lengths = [len(row.split(delimiter)) for row in result if row[0:5] == "stand"]
        tree_row_lengths = [len(row.split(delimiter)) for row in result if row[0:4] == "tree"]
        stratum_rows_lengths = [len(row.split(delimiter)) for row in result if row[0:7] == "stratum"]

        self.assertTrue(all(length == stand_row_lengths[0] for length in stand_row_lengths))
        self.assertTrue(all(length == tree_row_lengths[0] for length in tree_row_lengths))
        self.assertTrue(all(length == stratum_rows_lengths[0] for length in stratum_rows_lengths))

    def test_csv_to_stands(self):
        """tests that the roundtrip conversion stands-->csv-->stands maintains the stand structure"""
        vmi13_stands = vmi13_builder.build()
        vectorize(vmi13_stands)
        delimiter = ";"
        serialized = '\n'.join(stands_to_csv_content(ExportableContainer(vmi13_stands, None), delimiter))
        deserialized = list(csv.reader(StringIO(serialized), delimiter=delimiter))
        stands_from_csv = csv_content_to_stands(deserialized)
        vectorize(stands_from_csv)
        self.assertEqual(4, len(stands_from_csv))

        # Test that the stands from csv and the original stands are equal.
        # Perform comparison of dicts for each relevant object, setting relations to None to avoid recursive loop
        for i, stand in enumerate(vmi13_stands):
            for attribute in ["tree_number",
                              "species",
                              "breast_height_diameter",
                              "height",
                              "measured_height",
                              "breast_height_age",
                              "biological_age",
                              "stems_per_ha",
                              "origin",
                              "management_category",
                              "saw_log_volume_reduction_factor",
                              "pruning_year",
                              "age_when_10cm_diameter_at_breast_height",
                              "stand_origin_relative_position",
                              "lowest_living_branch_height",
                              "storey"]:
                self.assertTrue(
                    np.array_equal(
                        getattr(stand.reference_trees, attribute),
                        getattr(stands_from_csv[i].reference_trees, attribute), True))

            for attribute in ["identifier",
                              "sapling",
                              "tree_type",
                              "tree_category",
                              "tuhon_ilmiasu"]:
                self.assertTrue(np.all(
                    np.equal(
                        getattr(stand.reference_trees, attribute),
                        getattr(stands_from_csv[i].reference_trees, attribute))))

            for attribute in ["species",
                              "mean_diameter",
                              "mean_height",
                              "breast_height_age",
                              "biological_age",
                              "stems_per_ha",
                              "basal_area",
                              "origin",
                              "management_category",
                              "saw_log_volume_reduction_factor",
                              "cutting_year",
                              "age_when_10cm_diameter_at_breast_height",
                              "tree_number",
                              "stand_origin_relative_position",
                              "lowest_living_branch_height",
                              "storey",
                              "sapling_stems_per_ha",
                              "number_of_generated_trees"]:
                self.assertTrue(
                    np.array_equal(
                        getattr(stand.tree_strata, attribute),
                        getattr(stands_from_csv[i].tree_strata, attribute), True))

            for attribute in ["identifier", "sapling_stratum"]:
                self.assertTrue(
                    np.array_equal(
                        getattr(stand.tree_strata, attribute),
                        getattr(stands_from_csv[i].tree_strata, attribute)))

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
