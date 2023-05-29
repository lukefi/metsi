import unittest
from lukefi.metsi.forestry.preprocessing import age_supplementing as age_sup
from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from collections import namedtuple


def create_test_trees(inputs):
    data = []
    for i in inputs:
        tree = ReferenceTree()
        tree.identifier = i.id
        tree.species = i.species
        tree.breast_height_diameter = i.diameter
        tree.breast_height_age = i.breast_height_age
        tree.biological_age = i.biological_age
        tree.height = i.height
        data.append(tree)
    return data


def create_test_stratums(inputs):
    data = []
    for i in inputs:
        stratum = TreeStratum()
        stratum.identifier = i.id
        stratum.species = i.species
        stratum.mean_diameter = i.diameter
        stratum.breast_height_age = i.breast_height_age
        stratum.biological_age = i.biological_age
        data.append(stratum)
    return data


Input = namedtuple("Input", "id species diameter breast_height_age biological_age height")
age_tree_inputs = [
    Input('002-002-02-1-01-tree', 1, 10.0, 5, 8, None),
    Input('002-002-02-2-02-tree', 1, 10.0, 55, 88, None),
    Input('002-002-02-3-03-tree', 2, 10.0, 555, 888, None),
    Input('002-002-02-4-04-tree', 2, 10.0, 5555, 8888, None)
]
age_stratum_inputs = [
    Input('003-003-03-1-01-stratum', 1, 12.0, 6, 7, None),
    Input('003-003-03-2-02-stratum', 2, 0.0, 66, 77, None),
]
no_age_tree_inputs = [
    Input('001-001-01-1-01-tree', 1, 10.0, None, None, None),
    Input('001-001-01-2-02-tree', 2, 10.0, None, None, None),
    Input('001-001-01-3-03-tree', 3, 10.0, None, None, None),
    Input('001-001-01-4-04-tree', 4, 10.0, None, 0.1, None)
]
age_trees = create_test_trees(age_tree_inputs)
age_stratums = create_test_stratums(age_stratum_inputs)


class TestAgeSupplementing(unittest.TestCase):
    def test_final_tree_strategy(self):
        local_no_age_tree_inputs = [
            Input('001-001-01-3-03-tree', 3, 10.0, None, None, None),
            Input('001-001-01-4-04-tree', 4, 10.0, None, 0.1, None)
        ]
        no_age_trees = create_test_trees(local_no_age_tree_inputs)

        expectiations = [
            (True, 3),
            (True, 4)
        ]
        for i, e in enumerate(expectiations):
            strategy = age_sup.final_tree_strategy(no_age_trees[i])
            self.assertEqual(strategy.solved, e[0])
            self.assertEqual(strategy.strategy, e[1])
        # Also test for a failure case
        fail_tree = ReferenceTree()
        fail_tree.biological_age = 0.1
        fail_tree.height = 1.31
        fail_strategy = age_sup.final_tree_strategy(fail_tree)
        self.assertEqual(fail_strategy.solved, False)
        self.assertEqual(fail_strategy.strategy, None)

    def test_tree_strategy(self):
        local_no_age_tree_inputs = [
            Input('001-001-01-2-02-tree', 2, 10.0, None, None, None),
            Input('001-001-01-3-03-tree', 3, 10.0, None, None, None),
        ]
        no_age_trees = create_test_trees(local_no_age_tree_inputs)

        expectiations = [
            (True, 2),
            (False, None)
        ]
        for i, e in enumerate(expectiations):
            strategy = age_sup.tree_strategy(no_age_trees[i], age_trees)
            self.assertEqual(strategy.solved, e[0])
            self.assertEqual(strategy.strategy, e[1])

    def test_stratum_strategy(self):
        local_no_age_tree_inputs = [
            Input('001-001-01-1-01-tree', 1, 10.0, None, None, None),
            Input('001-001-01-2-02-tree', 2, 10.0, None, None, None),
        ]

        no_age_trees = create_test_trees(local_no_age_tree_inputs)

        expectiations = [
            (True, 1),
            (False, None)
        ]
        for i, e in enumerate(expectiations):
            strategy = age_sup.stratum_strategy(no_age_trees[i], age_stratums)
            self.assertEqual(strategy.solved, e[0])
            self.assertEqual(strategy.strategy, e[1])

    def test_solve_supplement_strategy(self):
        no_age_trees = create_test_trees(no_age_tree_inputs)

        expectations = [
            (True, age_sup.STRATUM_SUPPLEMENT),
            (True, age_sup.INITIAL_TREE_SUPPLEMENT),
            (True, age_sup.SAME_TREE_DIAMETER_SUPPLEMENT),
            (True, age_sup.SAME_TREE_D13_AGE_SUPPLEMENT)
        ]

        tree_and_strategies = age_sup.solve_supplement_strategy(no_age_trees,
                                                                age_trees,
                                                                age_stratums)

        for i, e in enumerate(expectations):
            self.assertEqual(tree_and_strategies[i][1].solved, e[0])
            self.assertEqual(tree_and_strategies[i][1].strategy, e[1])

    def test_perform_supplementing(self):
        no_age_trees = create_test_trees(no_age_tree_inputs)

        expectations = [
            (6, 7),  # INITIAL_STRATUM
            (555, 888),  # INITIAL_TREE_SUPPLEMENT
            (10.0 * 2, 10.0 * 2 + 9),  # SAME_TREE_DIAMETER_SUPPLEMENT
            (10.0 * 2, 20.0 + 9)  # SAME_TREE_D13_AGE_SUPPLEMENT
        ]

        tree_and_strategies = age_sup.solve_supplement_strategy(no_age_trees,
                                                                age_trees,
                                                                age_stratums)

        age_sup.perform_supplementing(tree_and_strategies, age_trees, age_stratums)

        for i, e in enumerate(expectations):
            self.assertEqual(no_age_trees[i].breast_height_age, e[0])
            self.assertEqual(no_age_trees[i].biological_age, e[1])

    def test_supplement_age_for_reference_trees(self):
        tree_values = [
            Input('002-002-02-1-01-tree', 1, 10.0, None, 2, 1.3), # sapling, not to be included in results
            Input('002-002-02-2-02-tree', 1, 10.0, None, 5, 3.5),
            Input('002-002-02-3-03-tree', 2, 10.0, None, 12, 8.0),
            Input('002-002-02-4-04-tree', 2, 10.0, None, 15, 12.0),
            # do not need age supplementing
            Input('002-002-02-5-05-tree', 1, 10.0, 5, 8, 9),
            Input('002-002-02-6-06-tree', 2, 10.0, 5, 8, 9)
        ]
        input_trees = create_test_trees(tree_values)
        input_stratums = create_test_stratums(age_stratum_inputs)
        result = age_sup.supplement_age_for_reference_trees(input_trees, input_stratums)
        self.assertEqual(3, len(result))
        self.assertEqual(6, result[0].breast_height_age)
        self.assertEqual('002-002-02-2-02-tree', result[0].identifier)
        self.assertEqual(5, result[1].breast_height_age)
        self.assertEqual('002-002-02-3-03-tree', result[1].identifier)
        self.assertEqual(5, result[2].breast_height_age)
        self.assertEqual('002-002-02-4-04-tree', result[2].identifier)
        # test that the sapling 002-002-02-1-01-tree is not included in results
        result = [tree for tree in result if tree.identifier == input_trees[0].identifier]
        self.assertEqual(0, len(result))
