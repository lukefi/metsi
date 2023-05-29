
import unittest
import lukefi.metsi.domain.pre_ops as preprocessing
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.data.enums.internal import TreeSpecies

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

    def test_generate_reference_trees(self):
        """ In this suite there are two stratum fixture cases.
        A stratum that has all necessary attributes inflated and one that needs mean diameter to be supplemented
        """
        normal_case = TreeStratum(mean_diameter=17.0, mean_height=15.0, basal_area=250.0, stems_per_ha=None, biological_age=10.0)
        supplement_diameter_case = TreeStratum(mean_diameter=None, mean_height=25.0, basal_area=250.0, stems_per_ha=300.0, biological_age=15.0)
        fixtures = [normal_case, supplement_diameter_case]
        stand = ForestStand()
        stand.identifier = 'xxx'
        stand.tree_strata.extend(fixtures)
        result = preprocessing.generate_reference_trees([stand], n_trees=10)
        self.assertEqual(20, len(result[0].reference_trees))
        self.assertEqual('xxx-1-tree', result[0].reference_trees[0].identifier)
        self.assertEqual('xxx-2-tree', result[0].reference_trees[1].identifier)
        self.assertEqual('xxx-11-tree', result[0].reference_trees[10].identifier)
        self.assertEqual('xxx-12-tree', result[0].reference_trees[11].identifier)
        self.assertEqual(10237.96, result[0].reference_trees[0].stems_per_ha)
        self.assertEqual(1138.02, result[0].reference_trees[1].stems_per_ha)
        self.assertEqual(2768.41, result[0].reference_trees[10].stems_per_ha)
        self.assertEqual(982.96, result[0].reference_trees[11].stems_per_ha)


    def test_determine_tree_height(self):
        stand = ForestStand()
        stand.reference_trees.append(ReferenceTree(breast_height_diameter=20.0, species=TreeSpecies.SPRUCE))
        stand.reference_trees.append(ReferenceTree(breast_height_diameter=0.0, species=TreeSpecies.OAK))
        result, = preprocessing.supplement_missing_tree_heights([stand])
        self.assertEqual(result.reference_trees[0].height, 17.1)
        self.assertEqual(result.reference_trees[1].height, None)

    def test_determine_tree_age(self):
        stand = ForestStand()
        stand.reference_trees.append(ReferenceTree(height=25.0, breast_height_age=50.0, biological_age=59.0, species=TreeSpecies.PINE))
        stand.reference_trees.append(ReferenceTree(height=25.0, breast_height_age=None, biological_age=None, species=TreeSpecies.PINE))
        result, = preprocessing.supplement_missing_tree_ages([stand])
        self.assertEqual(result.reference_trees[1].breast_height_age, 50.0)
        self.assertEqual(result.reference_trees[1].biological_age, 59.0)

    def test_generate_sapling_trees_from_sapling_strata(self):
        stand = ForestStand()
        stand.tree_strata.append(TreeStratum(mean_diameter=2, mean_height=0.9, biological_age=5.0, sapling_stratum=True))
        result, = preprocessing.generate_sapling_trees_from_sapling_strata([stand])
        self.assertEqual(len(result.reference_trees), 1)
        self.assertEqual(result.reference_trees[0].sapling, True)
        self.assertEqual(result.reference_trees[0].breast_height_diameter, 2)
        self.assertEqual(result.reference_trees[0].height, 0.9)
