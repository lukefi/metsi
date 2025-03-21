import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from importlib.util import spec_from_file_location, module_from_spec
from lukefi.metsi.data.enums.internal import *
from lukefi.metsi.app import file_io
from dataclasses import dataclass
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum

from lukefi.metsi.app.app_io import MetsiConfiguration


@dataclass
class Test:
    a: int

    def __eq__(self, other):
        return self.a == other.a


class TestFileReading(unittest.TestCase):
    @unittest.skip
    def test_determine_file_path(self):
        assertions = [
            (('testdir', 'rst'), (
                Path('testdir', 'preprocessing_result.rst'),
                Path('testdir', 'preprocessing_result.rsts'))
            ),
            (('testdir', 'csv'), ( Path('testdir', 'preprocessing_result.csv'), )), # single tuple
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
        file_io.prepare_target_directory('outdir')
        file_io.pickle_writer(Path('outdir', 'output.pickle'), data)
        result = file_io.pickle_reader('outdir/output.pickle')
        self.assertListEqual(data, result)
        os.remove('outdir/output.pickle')
        shutil.rmtree('outdir')

    def test_json(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        file_io.prepare_target_directory('outdir')
        file_io.json_writer(Path('outdir', 'output.json'), data)
        result = file_io.json_reader('outdir/output.json')
        self.assertListEqual(data, result)
        os.remove('outdir/output.json')
        shutil.rmtree('outdir')

    @unittest.skip
    def test_csv(self):
        data = [
            ForestStand(
                identifier="123-234",
                geo_location=(600000.0, 300000.0, 30.0, "EPSG:3067"),
                reference_trees=[
                    ReferenceTree(
                        identifier="123-234-1",
                        species=TreeSpecies.PINE
                    )
                ]
            )
        ]
        file_io.prepare_target_directory("outdir")
        file_io.csv_writer(Path("outdir", "output.csv"), data)
        result = file_io.csv_content_to_stands(
            file_io.csv_file_reader(Path("outdir/output.csv")))
        data[0].reference_trees[0].stand = None
        result[0].reference_trees[0].stand = None
        self.assertDictEqual(data[0].reference_trees[0].__dict__, result[0].reference_trees[0].__dict__)
        data[0].reference_trees = []
        result[0].reference_trees = []
        self.assertDictEqual(data[0].__dict__, result[0].__dict__)
        shutil.rmtree('outdir')

    @unittest.skip
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
                reference_trees=[
                    ReferenceTree(
                        identifier="123-234-1",
                        species=TreeSpecies.PINE,
                        stems_per_ha=200.0,
                        sapling=False
                    )
                ]
            )
        ]
        file_io.prepare_target_directory("outdir")
        target = Path("outdir", "output.rst")
        file_io.rst_writer(target, data)

        #There is no rst input so check sanity just by file existence and non-emptiness
        exists = os.path.exists(target)
        size = os.path.getsize(target)
        self.assertTrue(exists)
        self.assertTrue(size > 0)
        shutil.rmtree('outdir')

    @unittest.skip
    def test_rsts(self):
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
                tree_strata=[
                    TreeStratum(
                        identifier="123-234-1",
                        tree_number=1,
                        species=TreeSpecies.PINE,
                        stems_per_ha=200.0,
                        mean_diameter=20.0,
                        mean_height=15.0,
                        breast_height_age=52,
                        biological_age=55,
                        basal_area=210.0,
                        sapling_stems_per_ha=100.0,
                        storey=Storey.DOMINANT
                    )
                ]
            )
        ]
        file_io.prepare_target_directory("outdir")
        target = Path("outdir", "output.rsts")
        file_io.rsts_writer(target, data)

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
        self.assertEqual(type(stands_from_json[0].tree_strata[0]), TreeStratum)

    def test_read_stands_from_csv_file(self):
        config = MetsiConfiguration(
            input_path="tests/resources/file_io_test/forest_centre.csv",
            state_format="fdm",
            state_input_container="csv"
        )
        stands_from_csv = file_io.read_stands_from_file(config, {})
        self.assertEqual(len(stands_from_csv), 2)
        self.assertEqual(type(stands_from_csv[0]), ForestStand)
        self.assertEqual(type(stands_from_csv[0].tree_strata[0]), TreeStratum)

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
        dir = Path("tests/resources/file_io_test/testing_output_directory/3/0")
        result = file_io.read_schedule_payload_from_directory(dir)
        self.assertEqual("3", result.computational_unit.identifier)
        self.assertEqual(2, len(result.collected_data.get_list_result("calculate_biomass")))

    def test_read_simulation_result_dirtree(self):
        dir = Path("tests/resources/file_io_test/testing_output_directory")
        result = file_io.read_full_simulation_result_dirtree(dir)
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
        with open(control_path, "w") as f:
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
