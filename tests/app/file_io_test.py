import unittest
import os
import shutil
from pathlib import Path
from forestdatamodel.enums.internal import TreeSpecies
import app.file_io
from dataclasses import dataclass
from forestdatamodel.model import ForestStand, ReferenceTree

from app.app_io import Mela2Configuration
from sim.core_types import OperationPayload


@dataclass
class Test:
    a: int

    def __eq__(self, other):
        return self.a == other.a


class TestFileReading(unittest.TestCase):
    def test_file_contents(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "file_io_test", "test_dummy")
        result = app.file_io.file_contents(input_file_path)
        self.assertEqual("kissa123\n", result)

    def test_simulation_declaration_from_yaml_file(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "file_io_test", "control.yaml")
        result = app.file_io.simulation_declaration_from_yaml_file(input_file_path)
        self.assertEqual(1, len(result.keys()))

    def test_pickle(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        app.file_io.prepare_target_directory('outdir')
        app.file_io.pickle_writer(Path('outdir', 'output.pickle'), data)
        result = app.file_io.pickle_reader('outdir/output.pickle')
        self.assertListEqual(data, result)
        os.remove('outdir/output.pickle')
        shutil.rmtree('outdir')

    def test_json(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        app.file_io.prepare_target_directory('outdir')
        app.file_io.json_writer(Path('outdir', 'output.json'), data)
        result = app.file_io.json_reader('outdir/output.json')
        self.assertListEqual(data, result)
        os.remove('outdir/output.json')
        shutil.rmtree('outdir')

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
        app.file_io.prepare_target_directory("outdir")
        app.file_io.csv_writer(Path("outdir", "output.csv"), data)
        result = app.file_io.csv_to_stands("outdir/output.csv", ";")
        self.assertListEqual(data, result)
        shutil.rmtree('outdir')

    def test_rsd(self):
        data = [
            ForestStand(
                identifier="123-234",
                geo_location=(600000.0, 300000.0, 30.0, "EPSG:3067"),
                land_use_category=2,
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
        app.file_io.prepare_target_directory("outdir")
        target = Path("outdir", "output.rsd")
        app.file_io.rsd_writer(target, data)

        #There is no rsd input so check sanity just by file existence and non-emptiness
        exists = os.path.exists(target)
        size = os.path.getsize(target)
        self.assertTrue(exists)
        self.assertTrue(size > 0)
        shutil.rmtree('outdir')

    def test_read_stands_from_pickle_file(self):
        config = Mela2Configuration(
            input_path="tests/resources/file_io_test/two_ffc_stands.pickle",
            state_format="fdm",
            state_input_container="pickle"
        )
        unpickled_stands = app.file_io.read_stands_from_file(config)
        self.assertEqual(len(unpickled_stands), 2)
        self.assertEqual(type(unpickled_stands[0]), ForestStand)

    def test_read_stands_from_json_file(self):
        config = Mela2Configuration(
            input_path="tests/resources/file_io_test/two_vmi12_stands_as_jsonpickle.json",
            state_format="fdm",
            state_input_container="json"
        )
        stands_from_json = app.file_io.read_stands_from_file(config)
        self.assertEqual(len(stands_from_json), 2)
        self.assertEqual(type(stands_from_json[0]), ForestStand)
        self.assertEqual(type(stands_from_json[1].reference_trees[0]), ReferenceTree)

    def test_read_stands_from_csv_file(self):
        config = Mela2Configuration(
            input_path="tests/resources/file_io_test/preprocessing_result.csv",
            state_format="fdm",
            state_input_container="csv"
        )
        stands_from_csv = app.file_io.read_stands_from_file(config)
        self.assertEqual(len(stands_from_csv), 1)
        self.assertEqual(type(stands_from_csv[0]), ForestStand)
        self.assertEqual(type(stands_from_csv[0].reference_trees[0]), ReferenceTree)

    def test_read_stands_from_vmi12_file(self):
        config = Mela2Configuration(
            input_path="tests/resources/file_io_test/VMI12_source_mini.dat",
            state_format="vmi12",
            state_input_container=""
        )
        stands = app.file_io.read_stands_from_file(config)
        self.assertEqual(len(stands), 7)

    def test_read_stands_from_vmi13_file(self):
        config = Mela2Configuration(
            input_path="tests/resources/file_io_test/VMI13_source_mini.dat",
            state_format="vmi13",
            state_input_container=""
        )
        stands = app.file_io.read_stands_from_file(config)
        self.assertEqual(len(stands), 3)

    def test_read_stands_from_xml_file(self):
        config = Mela2Configuration(
            input_path="tests/resources/file_io_test/SMK_source.xml",
            state_format="forest_centre",
            state_input_container=""
        )
        stands = app.file_io.read_stands_from_file(config)
        self.assertEqual(len(stands), 3)

    def test_read_schedule_payload_from_directory(self):
        dir = Path("tests/resources/file_io_test/testing_output_directory/3/0")
        result = app.file_io.read_schedule_payload_from_directory(dir)
        self.assertEqual("3", result.simulation_state.identifier)
        self.assertEqual(2, len(result.aggregated_results.get("report_biomass")))

    def test_read_simulation_result_dirtree(self):
        dir = Path("tests/resources/file_io_test/testing_output_directory")
        result = app.file_io.read_full_simulation_result_dirtree(dir)
        self.assertEqual(1, len(result.items()))
        self.assertEqual(1, len(result["3"]))
        self.assertEqual("3", result["3"][0].simulation_state.identifier)
        self.assertEqual(2, len(result["3"][0].aggregated_results.get("report_biomass")))

    def test_read_stands_from_nonexisting_file(self):
        config = Mela2Configuration(
            input_path="nonexisting_file.pickle",
            state_format="fdm",
            state_input_container="pickle"
        )
        self.assertRaises(Exception, app.file_io.read_stands_from_file, config)
        