
import unittest
import forestry.preprocessing as preprocessing
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies

def generate_stand_with_saplings(sapling_tree_count, reference_tree_count):
    """generates a ForestStand with a given number of ReferenceTrees of which a given number is sapling trees"""
    stand = ForestStand()
    for i in range(reference_tree_count):
        is_sapling = i < sapling_tree_count
        stand.reference_trees.append(ReferenceTree(sapling=is_sapling))
    return stand


def generate_empty_stands(stand_count, empty_stand_count):
    stands = []
    for i in range(0, stand_count):
        stand = ForestStand()
        stand_is_empty = i < empty_stand_count
        #if the stand is not meant to be empty, add one Reference tree.
        if not stand_is_empty:
            stand.reference_trees.append(ReferenceTree(species=TreeSpecies(1)))
        stands.append(stand)

    return stands

class PreprocessingTest(unittest.TestCase):

    def test_exclude_sapling_trees(self):
        sapling_tree_count = 2
        reference_tree_count = 4
        #create a list of one stand
        stands = [generate_stand_with_saplings(sapling_tree_count, reference_tree_count)]
        excluded = preprocessing.exclude_sapling_trees(stands)
        #count of reference trees in the stand after sapling exclusion should equal to the original count minus saplings
        self.assertEqual(len(excluded[0].reference_trees), reference_tree_count - sapling_tree_count)

    def test_exclude_empty_stands(self):
        stand_count = 4
        empty_stand_count = 2

        stands = generate_empty_stands(stand_count, empty_stand_count)
        excluded = preprocessing.exclude_empty_stands(stands)
        self.assertEqual(len(excluded), stand_count - empty_stand_count)

    def test_exclude_zero_stem_trees(self):
        fixture = ForestStand()
        fixture.reference_trees = [
            ReferenceTree(stems_per_ha=f)
            for f in [1,2,0,3]
        ]
        result = preprocessing.exclude_zero_stem_trees([fixture])
        self.assertEqual(3, len(result[0].reference_trees))
