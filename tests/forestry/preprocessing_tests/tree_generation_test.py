""" Tests suites for forestryfunctions.preprocessing.* modules """
import unittest
from collections import namedtuple
from lukefi.metsi.data.model import TreeStratum, ReferenceTree, ForestStand
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.forestry.preprocessing import tree_generation


class TestTreeGeneration(unittest.TestCase):

    Input = namedtuple("Input", "species diameter basal_area mean_height breast_height_age biological_age stand stems_per_ha sapling_stems_per_ha")

    def create_test_stratums(self, inputs):
        data = []
        for i in inputs:
            stratum = TreeStratum()
            stratum.species = i.species
            stratum.mean_diameter = i.diameter
            stratum.basal_area = i.basal_area
            stratum.mean_height = i.mean_height
            stratum.breast_height_age = i.breast_height_age
            stratum.biological_age = i.biological_age
            stratum.stand = i.stand
            stratum.stems_per_ha = i.stems_per_ha
            stratum.sapling_stems_per_ha = i.sapling_stems_per_ha
            stratum.sapling_stratum = False if i.sapling_stems_per_ha is None or i.sapling_stems_per_ha == 0 else True
            data.append(stratum)
        return data


    def test_trees_from_weibull(self):
        fixture = TreeStratum()
        fixture.mean_diameter = 28.0
        fixture.basal_area = 27.0
        fixture.mean_height = 22.0
        fixture.species = TreeSpecies.PINE
        n_trees = 10
        result = tree_generation.trees_from_weibull(fixture, n_trees=n_trees)
        self.assertEqual(10, len(result))
        self.assertEqual(14.67280367311326, result[0].breast_height_diameter)
        self.assertEqual(17.4, result[0].height)
        self.assertEqual(1.9357767362985978, result[0].stems_per_ha)

    def test_finalize_trees(self):
        stratum = TreeStratum()
        stratum.species = 1
        stratum.stand = '0-012-001-01-1'
        stratum.breast_height_age = 25.0
        stratum.biological_age = 32.0
        reference_trees = []
        for i in range(4):
            reference_trees.append(ReferenceTree())
        result = tree_generation.finalize_trees(reference_trees, stratum)
        self.assertEqual('0-012-001-01-1', result[0].stand)
        self.assertEqual('0-012-001-01-1', result[1].stand)
        self.assertEqual(1, result[0].species)
        self.assertEqual(1, result[1].species)
        self.assertEqual(25.0, result[0].breast_height_age)
        self.assertEqual(25.0, result[1].breast_height_age)
        self.assertEqual(32.0, result[0].biological_age)
        self.assertEqual(32.0, result[1].biological_age)
        self.assertEqual(1, result[0].tree_number)
        self.assertEqual(2, result[1].tree_number)

    def test_solve_tree_generation_strategy(self):
        # Test data generation
        stratum_inputs = [
            # mean_diameter=10.0;
            # mean_height=8.0;
            # basal_area=33.0
            self.Input(None, 10.0, 33.0, 8.0, None, None, None, None, None), # --> weibull distribution
            # mean_diameter=10.0;
            # mean_height=8.0;
            # stems_per_ha=55.0
            self.Input(None, 10.0, None, 8.0, None, None, None, 55.0, None), # --> sapling weibull distribution (big trees)
            # mean_height=1.2;
            # sapling_stems_per_ha=111.0
            self.Input(None, None, None, 1.2, None, None, None, None, 111.0), # --> sapling weibull distribution (small trees)
            # all values None
            self.Input(None, None, None,  None,  None,  None, None, None, None) # --> Skip tree generation
        ]
        strata = self.create_test_stratums(stratum_inputs)

        expected_values = [
            tree_generation.TreeStrategy.WEIBULL_DISTRIBUTION,
            tree_generation.TreeStrategy.HEIGHT_DISTRIBUTION,
            tree_generation.TreeStrategy.HEIGHT_DISTRIBUTION,
            tree_generation.TreeStrategy.SKIP,
        ]

        for stratum, expected in zip(strata, expected_values):
            result = tree_generation.solve_tree_generation_strategy(stratum)
            self.assertEqual(expected, result)

    def test_generate_reference_trees_from_tree_stratum(self):
        # Test data generation
        stand = ForestStand()
        stand.identifier = "0-023-002-02-1"
        stratum_inputs = [
            # species=1;
            # diameter=28.0;
            # basal_area=27.0;
            # mean_height=22.0;
            # breast_height_age=15;
            # biological_age=16;
            # stems_per_ha=None;
            # sapling_stems_per_ha=None;
            self.Input(TreeSpecies.PINE, 28.0, 27.0, 22.0, 15, 16, stand, None, None), # Tree generation from weibull distribution
            # species=1;
            # diameter=28.0;
            # basal_area=None;
            # mean_height=22.0;
            # breast_height_age=15;
            # biological_age=16;
            # stems_per_ha=99.0
            # sapling_stems_per_ha=99.0
            self.Input(TreeSpecies.PINE, 28.0, None, 22.0, 15, 16, stand, 99.0, None), # Tree generation from height distribution
            # species=1;
            self.Input(TreeSpecies.PINE, None, None, None, None, None, None, None, None), # Skip tree generation
        ]
        test_data = self.create_test_stratums(stratum_inputs)

        expected_results = [
            # n_trees=10;
            # ForestStand=stand;
            # species=1;
            [10, stand, TreeSpecies.PINE,
            # diameter=14.67;
            # height=17.83;
            # stems_per_ha=1.94;
            # breast_height_age=15;
            # biological_age=16;
            14.67, 17.4, 1.94, 15, 16, # result[0]
            # diameter=17.14;
            # height=19.08;
            # stems_per_ha=15.42;
            # breast_height_age=15;
            # biological_age=16;
            17.14, 18.61, 15.42, 15, 16], # result[1]
            # n_trees=10;
            # ForestStand=stand;
            # species=1;
            [10, stand, TreeSpecies.PINE,
            # diameter=28.0;
            # height=22.0;
            # stems_per_ha=9.9;
            # breast_height_age=15;
            # biological_age=16;
            22.27, 18.36, 9.9, 15, 16, # result[0]
            # diameter=28.0;
            # height=22.0;
            # stems_per_ha=9.9;
            # breast_height_age=15;
            # biological_age=16;
            26.18, 19.92, 9.9, 15, 16], # result[1]
            [] # Skip case
        ]

        # Derive results
        results = []
        for test_stratum in test_data:
            result = tree_generation.reference_trees_from_tree_stratum(test_stratum, n_trees=10)
            results.append(result)
        # Validate
        for (result, asse) in zip(results, expected_results):
            n_reference_trees = len(result)
            if n_reference_trees == 10:
                self.assertEqual(asse[0], n_reference_trees)
                self.assertEqual(asse[1], result[0].stand)
                self.assertEqual(asse[2], result[0].species)
                self.assertEqual(asse[3], result[0].breast_height_diameter)
                self.assertEqual(asse[4], result[0].height)
                self.assertEqual(asse[5], result[0].stems_per_ha)
                self.assertEqual(asse[6], result[0].breast_height_age)
                self.assertEqual(asse[7], result[0].biological_age)
                self.assertEqual(asse[8], result[1].breast_height_diameter)
                self.assertEqual(asse[9], result[1].height)
                self.assertEqual(asse[10], result[1].stems_per_ha)
                self.assertEqual(asse[11], result[1].breast_height_age)
                self.assertEqual(asse[12], result[1].biological_age)

            else:
                # Skip case
                self.assertEqual(0, n_reference_trees)

    def test_generate_sapling_reference_trees_from_tree_stratum(self):
        # Test data generation
        stand = ForestStand()
        stand.identifier = "0-023-002-02-1"
        stratum_inputs = [
            # species=1;
            # mean_diameter=1.0;
            # basal_area=0.0;
            # mean_height=1.3;
            # breast_height_age=0;
            # biological_age=5;
            # ForestStand=stand;
            # stems_per_ha=None
            # sapling_stems_per_ha=330.0
            self.Input(1,  0.0,  0.0,  1.3,  0,  5, stand, 330.0, 330.0), # Sapling tree generation
            # species=1;
            # all other values None
            # self.Input(1, None, None,  None,  None,  None, None, None, None) # Skip tree generation
        ]
        test_data = self.create_test_stratums(stratum_inputs)

        expected_results = [
            # n_trees=10;
            # ForestStand=stand;
            # species=1;
            # diameter=0.0;
            # height=1.3;
            # stems_per_ha=33.0;
            # breast_height_age=0.0;
            # biological_age=5;
            [10, stand, 1, 1.0, 1.3, 33.0, 0.0, 5],
            # n_trees=0
            # List[ReferenceTree]=[]
            [0, []],
        ]

        # Derive results
        n_trees = 10
        results = []
        for test_stratum in test_data:
            result = tree_generation.reference_trees_from_tree_stratum(test_stratum, n_trees=n_trees)
            results.append(result)
        # Validate
        for (result, asse) in zip(results, expected_results):
            n_reference_trees = len(result)
            self.assertEqual(asse[0], n_reference_trees)
            if n_reference_trees == 1:
                self.assertEqual(asse[1], result[0].stand)
                self.assertEqual(asse[2], result[0].species)
                self.assertEqual(asse[3], round(result[0].breast_height_diameter,2))
                self.assertEqual(asse[4], round(result[0].height,2))
                self.assertEqual(asse[5], round(result[0].stems_per_ha,2))
                self.assertEqual(asse[6], result[0].breast_height_age)
                self.assertEqual(asse[7], result[0].biological_age)
