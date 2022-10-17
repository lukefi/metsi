import unittest
import os
import app.file_io
from dataclasses import dataclass
from forestdatamodel.model import ForestStand, ReferenceTree


@dataclass
class Test:
    a: int

    def __eq__(self, other):
        return self.a == other.a


class TestFileReading(unittest.TestCase):
    def test_file_contents(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "test_dummy")
        result = app.file_io.file_contents(input_file_path)
        self.assertEqual("kissa123\n", result)

    def test_simulation_declaration_from_yaml_file(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "control.yaml")
        result = app.file_io.simulation_declaration_from_yaml_file(input_file_path)
        self.assertEqual(2, len(result.keys()))

    def test_pickle(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        app.file_io.pickle_writer('testpickle', data)
        result = app.file_io.pickle_reader('testpickle')
        self.assertListEqual(data, result)
        os.remove('testpickle')

    def test_json(self):
        data = [
            Test(a=1),
            Test(a=2)
        ]
        app.file_io.json_writer('testjson', data)
        result = app.file_io.json_reader('testjson')
        self.assertListEqual(data, result)
        os.remove('testjson')

    def test_read_stands_from_pickle_file(self):
        unpickled_stands = app.file_io.read_payload_input_file("tests/resources/two_ffc_stands.pickle", "pickle")
        self.assertEqual(len(unpickled_stands), 2)
        self.assertEqual(type(unpickled_stands[0]), ForestStand)

    def test_read_stands_from_json_file(self):
        stands_from_json = app.file_io.read_payload_input_file("tests/resources/two_vmi12_stands_as_jsonpickle.json", "json")
        self.assertEqual(len(stands_from_json), 2)
        self.assertEqual(type(stands_from_json[0]), ForestStand)
        self.assertEqual(type(stands_from_json[1].reference_trees[0]), ReferenceTree)

    def test_read_stands_from_vmi12_file(self):
        stands = app.file_io.read_payload_input_file("tests/resources/VMI12_source_mini.dat", "vmi12")
        self.assertEqual(len(stands), 7)

    def test_read_stands_from_vmi13_file(self):
        stands = app.file_io.read_payload_input_file("tests/resources/VMI13_source_mini.dat", "vmi13")
        self.assertEqual(len(stands), 3)

    def test_read_stands_from_xml_file(self):
        stands = app.file_io.read_payload_input_file("tests/resources/SMK_source.xml", "forest_centre")
        self.assertEqual(len(stands), 3)

    def test_read_operation_payloads_from_pickle_file(self):
        data: dict = app.file_io.read_simulation_results_input_file("tests/resources/post_processing_input_one_vmi12_stand_nine_schedules.pickle", "pickle")
        self.assertFalse(data.get('0-023-002-02-1') is None)
        self.assertEqual(len(data.get('0-023-002-02-1')), 9)

    def test_read_stands_from_nonexisting_file(self):
        kwargs = {
            "file_path": "tests/resources/nonexisting_file.pickle",
            "input_format": "pickle"
        }
        self.assertRaises(Exception, app.file_io.read_payload_input_file, **kwargs)

    def test_write_stands_to_file(self):
        stands = [
            ForestStand(
                reference_trees=[
                    ReferenceTree(identifier=1)
                ]
            ),
            ForestStand(
                reference_trees=[
                    ReferenceTree(identifier=2)
                ]
            )
        ]
        app.file_io.write_result_to_file(stands, "tests/resources/temp_two_stands.pickle", "pickle")
        self.assertTrue(os.path.isfile("tests/resources/temp_two_stands.pickle"))
        os.remove("tests/resources/temp_two_stands.pickle")

        app.file_io.write_result_to_file(stands, "tests/resources/temp_two_stands.json", "json")
        self.assertTrue(os.path.isfile("tests/resources/temp_two_stands.json"))
        os.remove("tests/resources/temp_two_stands.json")

        #write_result_to_file should raise an Exception if the given output_format is not supported
        self.assertRaises(Exception, app.file_io.write_result_to_file, stands, "tests/resources/temp_two_stands.txt", "txt")

        