import unittest

from lukefi.metsi.sim.generators import sequence, alternatives
from lukefi.metsi.sim.runners import evaluate_sequence
from lukefi.metsi.sim.core_types import EventTree, SimConfiguration
from tests.test_utils import inc


class ComputationModelTest(unittest.TestCase):
    root = EventTree(inc)
    root.branches = [
        EventTree(inc),
        EventTree(inc)
    ]

    root.branches[0].branches = [
        EventTree(inc),
        EventTree(inc)
    ]

    root.branches[1].branches = [
        EventTree(inc),
        EventTree(inc)
    ]

    def test_event_generating(self):
        chains = self.root.operation_chains()
        self.assertEqual(4, len(chains))
        self.assertEqual(3, len(chains[0]))
        self.assertEqual(3, len(chains[1]))

    def test_run_chains(self):
        chains = self.root.operation_chains()
        for chain in chains:
            result = evaluate_sequence(0, *chain)
            self.assertEqual(3, result)

    def test_evaluator(self):
        results = self.root.evaluate(0)
        self.assertListEqual([3, 3, 3, 3], results)

    def test_sim_configuration(self):
        fn1 = lambda x: x
        fn2 = lambda y: y
        operation_lookup = {
            'operation1': fn1,
            'operation2': fn2
        }
        generator_lookup = {
            'sequence': sequence,
            'alternatives': alternatives
        }
        config = {
            'operation_params': {
                'operation1': [{'param1': 1}]
            },
            'run_constraints': {
                'operation1': {
                    'minimum_time_interval': 5
                }
            },
            'simulation_events': [
                {
                    'time_points': [1, 2, 3],
                    'generators': [
                        'operation1',
                        'operation2'
                    ]
                },
                {
                    'time_points': [3, 4, 5],
                    'generators': [
                        {
                            'sequence': [
                                'operation1',
                                'operation2'
                            ]
                        }
                    ]
                }
            ]
        }
        result = SimConfiguration(operation_lookup=operation_lookup, generator_lookup=generator_lookup, **config)
        self.assertListEqual([1, 2, 3, 4, 5], result.time_points)
        self.assertEqual(2, len(result.events))
        self.assertEqual(fn1, result.operation_lookup.get('operation1'))
        self.assertEqual(fn2, result.operation_lookup.get('operation2'))
        self.assertDictEqual(generator_lookup, result.generator_lookup)
        self.assertDictEqual(operation_lookup, result.operation_lookup)
        self.assertDictEqual({'operation1': {'minimum_time_interval': 5}}, result.run_constraints)
