import unittest

from lukefi.metsi.sim.state_tree import StateTree


def testing_operation(op_tuple: tuple[list[int], list[int]], **params) -> tuple[list[int], list[int]]:
    state, collected_data = op_tuple
    for i, _ in enumerate(state):
        state[i] += params.get("increment", 1)
        collected_data[i] += state[i] * params.get("mult", 1)
    return state, collected_data


class StateTreeTest(unittest.TestCase):
    def test_init(self):
        state = [0, 0, 0]
        parameters = {"increment": 2, "mult": 2}
        state_tree = StateTree(state, testing_operation, 1, parameters)

        self.assertListEqual(state_tree.state, state)
        self.assertEqual(state_tree.done_operation, testing_operation)
        self.assertEqual(state_tree.time_point, 1)
        self.assertDictEqual(state_tree.operation_params, parameters)
        self.assertListEqual(state_tree.branches, [])

    def test_add_branch(self):
        state = [0, 0, 0]
        parameters = {"increment": 2, "mult": 2}
        state, _ = testing_operation((state, [0, 0, 0]), increment=2, mult=2)
        state_tree = StateTree(state, testing_operation, 1, parameters)
        state = state.copy()
        state_tree.add_branch(StateTree(testing_operation((state, [0, 0, 0]), increment=2, mult=1)[
                              0], testing_operation, 2, {"increment": 2, "mult": 1}))

        self.assertListEqual(state_tree.state, [2, 2, 2])
        self.assertEqual(state_tree.done_operation, testing_operation)
        self.assertEqual(state_tree.time_point, 1)
        self.assertDictEqual(state_tree.operation_params, parameters)
        self.assertEqual(len(state_tree.branches), 1)

        self.assertListEqual(state_tree.branches[0].state, [4, 4, 4])
        self.assertEqual(state_tree.branches[0].done_operation, testing_operation)
        self.assertEqual(state_tree.branches[0].time_point, 2)
        self.assertDictEqual(state_tree.branches[0].operation_params, {"increment": 2, "mult": 1})
        self.assertEqual(len(state_tree.branches[0].branches), 0)
