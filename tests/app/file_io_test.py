import unittest
import os
import shutil
from pathlib import Path
import app.file_io
from dataclasses import dataclass
from forestdatamodel.model import ForestStand, ReferenceTree
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

    def test_read_stands_from_pickle_file(self):
        unpickled_stands = app.file_io.read_stands_from_file("tests/resources/file_io_test/two_ffc_stands.pickle", "fdm", "pickle")
        self.assertEqual(len(unpickled_stands), 2)
        self.assertEqual(type(unpickled_stands[0]), ForestStand)

    def test_read_stands_from_json_file(self):
        stands_from_json = app.file_io.read_stands_from_file("tests/resources/file_io_test/two_vmi12_stands_as_jsonpickle.json", "fdm", "json")
        self.assertEqual(len(stands_from_json), 2)
        self.assertEqual(type(stands_from_json[0]), ForestStand)
        self.assertEqual(type(stands_from_json[1].reference_trees[0]), ReferenceTree)

    def test_read_stands_from_csv_file(self):
        stands_from_csv = app.file_io.read_stands_from_file("tests/resources/file_io_test/preprocessing_result.csv", "fdm", "csv")
        self.assertEqual(len(stands_from_csv), 1)
        self.assertEqual(type(stands_from_csv[0]), ForestStand)
        self.assertEqual(type(stands_from_csv[0].reference_trees[0]), ReferenceTree)

    def test_read_stands_from_vmi12_file(self):
        stands = app.file_io.read_stands_from_file("tests/resources/file_io_test/VMI12_source_mini.dat", "vmi12", "")
        self.assertEqual(len(stands), 7)

    def test_read_stands_from_vmi13_file(self):
        stands = app.file_io.read_stands_from_file("tests/resources/file_io_test/VMI13_source_mini.dat", "vmi13", "")
        self.assertEqual(len(stands), 3)

    def test_read_stands_from_xml_file(self):
        stands = app.file_io.read_stands_from_file("tests/resources/file_io_test/SMK_source.xml", "forest_centre", "")
        self.assertEqual(len(stands), 3)

    def test_read_schedule_payload_from_directory(self):
        dir = Path("tests/resources/file_io_test/testing_output_directory/0-023-002-02-1/1")
        result = app.file_io.read_schedule_payload_from_directory(dir)
        self.assertEqual("0-023-002-02-1", result.simulation_state.identifier)
        self.assertEqual(2, len(result.aggregated_results.get("report_biomass")))

    def test_read_simulation_result_dirtree(self):
        dir = Path("tests/resources/file_io_test/testing_output_directory")
        result = app.file_io.read_full_simulation_result_dirtree(dir)
        self.assertEqual(1, len(result.items()))
        self.assertEqual(2, len(result["0-023-002-02-1"]))
        self.assertEqual("0-023-002-02-1", result["0-023-002-02-1"][0].simulation_state.identifier)
        self.assertEqual(2, len(result["0-023-002-02-1"][0].aggregated_results.get("report_biomass")))
        self.assertEqual("0-023-002-02-1", result["0-023-002-02-1"][1].simulation_state.identifier)
        self.assertEqual(2, len(result["0-023-002-02-1"][1].aggregated_results.get("report_biomass")))

    def test_read_stands_from_nonexisting_file(self):
        kwargs = {
            "file_path": "nonexisting_file.pickle",
            "state_format": "fdm",
            "state_input_container": "pickle"
        }
        self.assertRaises(Exception, app.file_io.read_stands_from_file, **kwargs)
        