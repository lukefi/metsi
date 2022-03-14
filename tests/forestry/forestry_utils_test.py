import unittest
import forestry.forestry_utils as f_util

from forestry.ForestDataModels import ForestStand, ReferenceTree

class ForestryUtilsTest(unittest.TestCase):
    def test_calculate_basal_area(self):
        tree = ReferenceTree()
        tree.breast_height_diameter = 10.0
        tree.stems_per_ha = 50.0
        result = f_util.calculate_basal_area(tree)
        self.assertEquals(0.3927, round(result, 4))

    def test_solve_dominant_height(self):
        reference_trees = []
        for i in range(1, 6):
            reference_tree = ReferenceTree()
            reference_tree.height = 28.0 + i
            reference_trees.append(reference_tree)
        # heights are [29.0, 30.0, 31.0, 32.0, 33.0]
        result = f_util.solve_dominant_height(reference_trees)
        self.assertEquals(31.0, result)

    def test_filter_reference_trees_by_species(self):
        reference_trees = []
        species = [1, 1, 2, 3, 3]
        for i in range(0, 5):
            reference_tree = ReferenceTree()
            reference_tree.species = species[i]
            reference_trees.append(reference_tree)
        result = f_util.filter_reference_trees_by_species(reference_trees)
        self.assertEquals(3, len(result))
        self.assertEquals(1, result[0][0].species)
        self.assertEquals(2, result[1][0].species)
        self.assertEquals(3, result[2][0].species)

    def test_calcualte_attribute_sum(self):
        f = lambda x: x.stems_per_ha
        reference_trees = []
        for i in range(1, 6):
            reference_tree = ReferenceTree()
            reference_tree.stems_per_ha = 2.0 * i
            reference_trees.append(reference_tree)
        # stems_per_ha are [2, 4, 6, 8, 10]
        result = f_util.calculate_attribute_sum(reference_trees, f)
        self.assertEquals(30, result)

    def test_calculate_basal_area_weighted_attribute_aggregate(self):
        """ Tests the generic function calculate_attribute_aggregate by counting the basal area weighted sum for breast height diameter for pine (species==1) """
        f = lambda x: x.breast_height_diameter * f_util.calculate_basal_area(x)
        reference_trees = []
        for i in range(1, 6):
            reference_tree = ReferenceTree()
            reference_tree.species = 1
            reference_tree.breast_height_diameter = 10.0 + i
            reference_tree.stems_per_ha = 50.0 + i
            reference_trees.append(reference_tree)
        result = f_util.calculate_basal_area_weighted_attribute_aggregate(reference_trees, f)
        self.assertEquals(13.3402, round(result,4))


