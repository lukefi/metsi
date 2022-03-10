import unittest

from forestry.ForestDataModels import ForestStand, ReferenceTree
from forestry.operations import grow


class ForestryOperationsTest(unittest.TestCase):
    def test_grow(self):
        species = [1, 1, 2, 3, 3]
        reference_trees = []
        for i in range(0, 5):
            reference_tree = ReferenceTree()
            reference_tree.species = species[i]
            reference_tree.breast_height_diameter = 10.0 + i
            reference_tree.stems_per_ha = 50.0 + i
            reference_tree.height = 28.0 + i
            reference_tree.biological_age = 20.0 + i
            reference_trees.append(reference_tree)
        stand = ForestStand()
        stand.reference_trees = reference_trees
        result_stand = grow(stand)
        self.assertEquals(5, len(result_stand.reference_trees))
        self.assertEquals(13.1827, round(result_stand.reference_trees[0].breast_height_diameter, 4))
        self.assertEquals(29.8520, round(result_stand.reference_trees[0].height, 4))
        self.assertEquals(14.4723, round(result_stand.reference_trees[1].breast_height_diameter, 4))
        self.assertEquals(30.8415, round(result_stand.reference_trees[1].height, 4))

