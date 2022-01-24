import unittest
import os

from sim.read_input import read_forest_json
from sim.ForestDataModels import ForestStand, ReferenceTree

absolute_resource_path = os.path.join(os.getcwd(), 'tests', 'resources')

class TestFileReading(unittest.TestCase):
    def test_read_forest_json(self):
        input_filename = "vmi13_small.json"
        input_file_path = absolute_resource_path + "/" + input_filename
        stands = read_forest_json(input_file_path)
        self.assertEqual(type(stands[0]), ForestStand)
        self.assertEqual(len(stands), 5)
        self.assertEqual(stands[0].identifier, "77-57-2-1")
        self.assertEqual(type(stands[0].reference_trees[0]), ReferenceTree)
        self.assertEqual(stands[1].reference_trees[0].identifier, "77-57-3-1-1-tree")
