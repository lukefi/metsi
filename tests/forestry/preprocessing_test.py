
import unittest
import forestry.preprocessing as preprocessing
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies

def generate_sapling_tree_stands(sapling_tree_count, reference_tree_count):
    """generates a ForestStand with a given number of ReferenceTrees of which a given number is sapling trees"""
    is_sapling_list = [True if i<=sapling_tree_count else False for i in range(1, reference_tree_count+1)]
    stand = ForestStand()
    stand.reference_trees = [ReferenceTree(sapling=s) for s in is_sapling_list]
    return stand

def generate_empty_stands(stand_count, empty_stand_count):
    is_empty_stand_list = [True if i<=empty_stand_count else False for i in range(1, stand_count+1)]
    stands = []
    for i in range(0, stand_count):
        stand = ForestStand()  
        stand_is_empty = is_empty_stand_list[i] 
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
        stands = [generate_sapling_tree_stands(sapling_tree_count, reference_tree_count)]
        excluded = preprocessing.exclude_sapling_trees(stands) #do not pass kwargs
        #count of reference trees in the stand after sapling exclusion should equal to the original count minus saplings
        self.assertEqual(len(excluded[0].reference_trees), reference_tree_count - sapling_tree_count)

    def test_exclude_empty_stands(self):
        stand_count = 4
        empty_stand_count = 2

        stands = generate_empty_stands(stand_count, empty_stand_count)
        excluded = preprocessing.exclude_empty_stands(stands) #do not pass kwargs
        self.assertEqual(len(excluded), stand_count - empty_stand_count)