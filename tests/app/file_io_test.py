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

    def test_forest_stands_from_json_file(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "vmi13_small.json")
        stands = app.file_io.forest_stands_from_json_file(input_file_path)
        self.assertEqual(type(stands[0]), ForestStand)
        self.assertEqual(len(stands), 5)
        self.assertEqual(stands[0].identifier, "77-57-2-1")
        self.assertEqual(type(stands[0].reference_trees[0]), ReferenceTree)
        self.assertEqual(stands[1].reference_trees[0].identifier, "77-57-3-1-1-tree")

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

    def test_read_stands_from_pickle_file(self):
        unpickled_stands = app.file_io.read_stands_from_file("tests/resources/two_ffc_stands.pickle", "pickle")
        self.assertEqual(len(unpickled_stands), 2)
        self.assertEqual(type(unpickled_stands[0]), ForestStand)

    def test_read_stands_from_json_file(self):
        stands_from_json = app.file_io.read_stands_from_file("tests/resources/vmi13_small.json", "json")
        self.assertEqual(len(stands_from_json), 5)
        self.assertEqual(type(stands_from_json[0]), ForestStand)

    def test_read_stands_from_nonexisting_file(self):
        failingFile = "nonexisting_file.txt"
        self.assertRaises(Exception, app.file_io.read_stands_from_file, failingFile)