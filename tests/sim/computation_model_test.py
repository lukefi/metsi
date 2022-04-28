import unittest
from sim.runners import evaluate_sequence
from sim.core_types import Step
from tests.test_utils import inc


class ComputationModelTest(unittest.TestCase):
    root = Step(inc)
    root.branches = [
        Step(inc),
        Step(inc)
    ]

    root.branches[0].branches = [
        Step(inc),
        Step(inc)
    ]

    root.branches[1].branches = [
        Step(inc),
        Step(inc)
    ]

    def test_step_generating(self):
        chains = self.root.operation_chains()
        self.assertEqual(4, len(chains))
        self.assertEqual(3, len(chains[0]))
        self.assertEqual(3, len(chains[1]))

    def test_run_chains(self):
        chains = self.root.operation_chains()
        for chain in chains:
            result = evaluate_sequence(0, *chain)
            self.assertEqual(3, result)
