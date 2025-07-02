import unittest

from lukefi.metsi.sim.state_tree import StateTree


def dummy_operation(op_tuple: tuple[list[int], list[int]], **params) -> tuple[list[int], list[int]]:
    state, collected_data = op_tuple
    for i, _ in enumerate(state):
        state[i] += params.get("increment", 1)
        collected_data[i] += state[i] * params.get("mult", 1)
    return state, collected_data


class StateTreeTest(unittest.TestCase):
    def test_init(self):
        state_tree: StateTree[list[int]] = StateTree()

        self.assertListEqual(state_tree.branches, [])

    def test_add_branch(self):
        state = [0, 0, 0]
        parameters = {"increment": 2, "mult": 2}
        state, _ = dummy_operation((state, [0, 0, 0]), increment=2, mult=2)
        state_tree: StateTree[list[int]] = StateTree()
        state_tree.state = state
        state_tree.operation_params = parameters
        state_tree.done_operation = dummy_operation
        state_tree.time_point = 1
        state = state.copy()

        parameters2 = {"increment": 2, "mult": 1}
        new_branch: StateTree[list[int]] = StateTree()
        new_branch.state = dummy_operation((state, [0, 0, 0]), **parameters2)[0]
        new_branch.operation_params = parameters2
        new_branch.done_operation = dummy_operation
        new_branch.time_point = 2

        state_tree.add_branch(new_branch)

        self.assertListEqual(state_tree.state, [2, 2, 2])
        self.assertEqual(state_tree.done_operation, dummy_operation)
        self.assertEqual(state_tree.time_point, 1)
        self.assertDictEqual(state_tree.operation_params, parameters)
        self.assertEqual(len(state_tree.branches), 1)

        self.assertListEqual(state_tree.branches[0].state, [4, 4, 4])
        self.assertEqual(state_tree.branches[0].done_operation, dummy_operation)
        self.assertEqual(state_tree.branches[0].time_point, 2)
        self.assertDictEqual(state_tree.branches[0].operation_params, parameters2)
        self.assertEqual(len(state_tree.branches[0].branches), 0)
