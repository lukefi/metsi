import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

import numpy as np
from lukefi.metsi.app import file_io
from lukefi.metsi.data.enums.internal import (DrainageCategory, LandUseCategory, OwnerCategory, SiteType,
                                              SoilPeatlandCategory, Storey, TreeSpecies)
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.app.app_types import ExportableContainer
from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.data.vectorize import vectorize


@dataclass
class Test:
    a: int

    def __eq__(self, other):
        return self.a == other.a


class TestFileReading(unittest.TestCase):

    def test_determine_file_path(self):
        assertions = [
            (('testdir', 'preprocessing_result.rst'), (Path('testdir', 'preprocessing_result.rst'))),
            (('testdir', 'preprocessing_result.csv'), (Path('testdir', 'preprocessing_result.csv')))
        ]
        for a in assertions:
            result = file_io.determine_file_path(*a[0])
            self.assertEqual(a[1], result)

    def test_file_contents(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "file_io_test", "test_dummy")
        result = file_io.file_contents(input_file_path)
        self.assertEqual("kissa123\n", result)

    def test_pickle(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        ec = ExportableContainer(export_objects=data, additional_vars=None)
        file_io.prepare_target_directory('outdir')
        file_io.pickle_writer(Path('outdir', 'output.pickle'), ec)
        result = file_io.pickle_reader('outdir/output.pickle')
        self.assertListEqual(data, result)
        os.remove('outdir/output.pickle')
        shutil.rmtree('outdir')

    def test_json(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        ec = ExportableContainer(export_objects=data, additional_vars=None)

        file_io.prepare_target_directory('outdir')
        file_io.json_writer(Path('outdir', 'output.json'), ec)
        result = file_io.json_reader('outdir/output.json')
        self.assertListEqual(data, result)
        os.remove('outdir/output.json')
        shutil.rmtree('outdir')

    def test_npy(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        ec = ExportableContainer(export_objects=data, additional_vars=None)

        file_io.prepare_target_directory('outdir')
        file_io.npy_writer(Path('outdir', 'output.npy'), ec)
        result = file_io.npy_file_reader('outdir/output.npy')
        self.assertListEqual(data, result.tolist())
        os.remove('outdir/output.npy')
        shutil.rmtree('outdir')

    def test_npz(self):
        data = [[
            Test(a=1),
            Test(a=2)
        ], [
            Test(a=3),
            Test(a=4)
        ]]
        ec = ExportableContainer(export_objects=data, additional_vars=None)

        file_io.prepare_target_directory('outdir')
        file_io.npz_writer(Path('outdir', 'output.npz'), ec)
        result = file_io.npz_file_reader('outdir/output.npz')
        self.assertListEqual(data, [subresult.tolist() for subresult in result])
        os.remove('outdir/output.npz')
        shutil.rmtree('outdir')

    def test_csv(self):
        data = [
            ForestStand(
                identifier="123-234",
                geo_location=(600000.0, 300000.0, 30.0, "EPSG:3067"),
                reference_trees_pre_vec=[
                    ReferenceTree(
                        identifier="123-234-1",
                        species=TreeSpecies.PINE
                    )
                ]
            )
        ]
        data = vectorize(data)
        ec = ExportableContainer(export_objects=data, additional_vars=None)

        file_io.prepare_target_directory("outdir")
        file_io.csv_writer(Path("outdir", "output.csv"), ec)
        result = vectorize(file_io.csv_content_to_stands(
            file_io.csv_file_reader(Path("outdir/output.csv"))))

        for i, stand in enumerate(data):
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
                        getattr(result[i].reference_trees, attribute), True))

            for attribute in ["identifier",
                              "sapling",
                              "tree_type",
                              "tree_category",
                              "tuhon_ilmiasu"]:
                self.assertTrue(np.all(
                    np.equal(
                        getattr(stand.reference_trees, attribute),
                        getattr(result[i].reference_trees, attribute))))

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
                        getattr(result[i].tree_strata, attribute), True))

            for attribute in ["identifier", "sapling_stratum"]:
                self.assertTrue(
                    np.array_equal(
                        getattr(stand.tree_strata, attribute),
                        getattr(result[i].tree_strata, attribute)))
        shutil.rmtree('outdir')

    def test_rst(self):
        data = [
            ForestStand(
                identifier="123-234",
                geo_location=(600000.0, 300000.0, 30.0, "EPSG:3067"),
                land_use_category=LandUseCategory.FOREST,
                owner_category=OwnerCategory.PRIVATE,
                soil_peatland_category=SoilPeatlandCategory.MINERAL_SOIL,
                site_type_category=SiteType.RICH_SITE,
                drainage_category=DrainageCategory.DITCHED_MINERAL_SOIL,
                fra_category="1",
                auxiliary_stand=False,
                reference_trees_pre_vec=[
                    ReferenceTree(
                        identifier="123-234-1",
                        species=TreeSpecies.PINE,
                        stems_per_ha=200.0,
                        sapling=False
                    )
                ]
            )
        ]
        ec = ExportableContainer(export_objects=data, additional_vars=None)

        file_io.prepare_target_directory("outdir")
        target = Path("outdir", "output.rst")
        file_io.rst_writer(target, ec)

        # There is no rst input so check sanity just by file existence and non-emptiness
        exists = os.path.exists(target)
        size = os.path.getsize(target)
        self.assertTrue(exists)
        self.assertTrue(size > 0)
        shutil.rmtree('outdir')


    def test_read_stands_from_pickle_file(self):
        config = MetsiConfiguration(
            input_path="tests/resources/file_io_test/forest_centre.pickle",
            state_format="fdm",
            state_input_container="pickle"
        )
        unpickled_stands = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(unpickled_stands), 2)
        self.assertEqual(type(unpickled_stands[0]), ForestStand)
        self.assertEqual(type(unpickled_stands[0].tree_strata[0]), TreeStratum)

    def test_read_stands_from_json_file(self):
        config = MetsiConfiguration(
            input_path="tests/resources/file_io_test/forest_centre.json",
            state_format="fdm",
            state_input_container="json"
        )
        stands_from_json = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands_from_json), 2)
        self.assertEqual(type(stands_from_json[0]), ForestStand)
        self.assertEqual(type(stands_from_json[0].tree_strata_pre_vec[0]), TreeStratum)

    def test_read_stands_from_csv_file(self):
        config = MetsiConfiguration(
            input_path="tests/resources/file_io_test/forest_centre.csv",
            state_format="fdm",
            state_input_container="csv"
        )
        stands_from_csv = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands_from_csv), 2)
        self.assertEqual(type(stands_from_csv[0]), ForestStand)
        self.assertEqual(type(stands_from_csv[0].tree_strata_pre_vec[0]), TreeStratum)

    def test_read_stands_from_vmi12_file(self):
        config = MetsiConfiguration(
            input_path="tests/resources/file_io_test/vmi12.dat",
            state_format="vmi12",
            state_input_container=""
        )
        stands = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands), 4)

    def test_read_stands_from_vmi13_file(self):
        config = MetsiConfiguration(
            input_path=Path("tests", "data", "resources", "VMI13_source_mini.dat"),
            state_format="vmi13",
            state_input_container=""
        )
        stands = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands), 4)

    def test_read_stands_from_xml_file(self):
        config = MetsiConfiguration(
            input_path="tests/resources/file_io_test/forest_centre.xml",
            state_format="xml",
            state_input_container=""
        )
        stands = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands), 2)

    def test_read_stands_from_gpkg_file(self):
        config = MetsiConfiguration(
            input_path="tests/data/resources/SMK_source.gpkg",
            state_format="gpkg",
            state_input_container=""
        )
        stands = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands), 9)

    def test_read_schedule_payload_from_directory(self):
        dir_ = Path("tests/resources/file_io_test/testing_output_directory/3/0")
        result = file_io.read_schedule_payload_from_directory(dir_)
        self.assertEqual("3", result.computational_unit.identifier)
        self.assertEqual(2, len(result.collected_data.get_list_result("calculate_biomass")))

    def test_read_simulation_result_dirtree(self):
        dir_ = Path("tests/resources/file_io_test/testing_output_directory")
        result = file_io.read_full_simulation_result_dirtree(dir_)
        self.assertEqual(1, len(result.items()))
        self.assertEqual(1, len(result["3"]))
        self.assertEqual("3", result["3"][0].computational_unit.identifier)
        self.assertEqual(2, len(result["3"][0].collected_data.get_list_result("calculate_biomass")))

    def test_read_stands_from_nonexisting_file(self):
        config = MetsiConfiguration(
            input_path="nonexisting_file.pickle",
            state_format="fdm",
            state_input_container="pickle"
        )
        self.assertRaises(Exception, file_io.read_stands_from_file, config)


class TestReadControlModule(unittest.TestCase):
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_read_control_module_success(self, mock_module_from_spec, mock_spec_from_file_location):
        # Mock the control module
        mock_spec = MagicMock()
        mock_loader = MagicMock()
        mock_spec.loader = mock_loader
        mock_spec_from_file_location.return_value = mock_spec

        mock_module = MagicMock()
        mock_module.control_structure = {"key": "value"}
        mock_module_from_spec.return_value = mock_module

        # Call the function
        control_path = str(Path("test_control.py").resolve())  # Resolve to absolute path
        result = file_io.read_control_module(control_path, "control_structure")

        # Assertions
        mock_spec_from_file_location.assert_called_once_with("test_control", control_path)
        mock_loader.exec_module.assert_called_once_with(mock_module)
        self.assertEqual(result, {"key": "value"})

    def test_read_control_module_attribute_error(self):
        control_path = os.path.join(os.getcwd(), "tests", "resources", "file_io_test", "dummy_control.py")
        with open(control_path, "w", encoding="utf-8") as f:
            f.write("some_variable = {'key': 'value'}")  # Create a dummy control file without the expected attribute

        with self.assertRaises(AttributeError) as context:
            file_io.read_control_module(control_path, control="nonexistent_control")

        self.assertIn("Variable 'nonexistent_control' not found", str(context.exception))
        os.remove(control_path)

    @patch("importlib.util.spec_from_file_location")
    def test_read_control_module_import_error(self, mock_spec_from_file_location):
        # Simulate an import error
        mock_spec_from_file_location.return_value = None

        # Call the function and expect an ImportError
        control_path = str(Path("test_control.py").resolve())  # Resolve to absolute path
        with self.assertRaises(ImportError):
            file_io.read_control_module(control_path, "control_structure")
