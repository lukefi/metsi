import unittest

from computation_model import Step
from sim.generators import instruction_with_options, sequence, compose
from sim.runners import sequence as run_sequence
from test_utils import inc


class TestGenerators(unittest.TestCase):
    def test_instruction_with_options(self):
        value = 100
        options = [10, 20, 30]
        func = lambda x, y: x + y
        prepared_functions = instruction_with_options(func, options)
        results = []
        for f in prepared_functions:
            results.append(f(value))
        self.assertEqual([110, 120, 130], results)

    def test_step_sequence_generating(self):
        root = Step()
        result = sequence(
            [root],
            inc,
            inc,
            inc
        )
        chain = root.operation_chains()[0]
        computation_result = run_sequence(0, *chain)
        self.assertEqual(3, computation_result)
        self.assertEqual(1, len(result))
        self.assertEqual(4, len(chain))

    def test_sequence_composition(self):
        generators = [
            lambda x: sequence(
                x,
                inc,
                inc
            ),
            lambda y: sequence(
                y,
                inc,
                inc
            )
        ]
        result = compose(*generators)
        chain = result.operation_chains()[0]
        computation_result = run_sequence(0, *chain)
        self.assertEqual(5, len(chain))
        self.assertEqual(4, computation_result)
