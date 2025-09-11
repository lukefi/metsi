import unittest

from lukefi.metsi.sim.event import Event
from lukefi.metsi.sim.generators import Sequence, Treatment
from lukefi.metsi.sim.runners import evaluate_sequence
from lukefi.metsi.sim.event_tree import EventTree
from lukefi.metsi.sim.sim_configuration import SimConfiguration
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
        def fn1(x): return x
        def fn2(y): return y
        operation_lookup = {
            'operation1': fn1,
            'operation2': fn2
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
                Event(
                    time_points=[1, 2, 3],
                    treatments=[
                        Treatment(
                            treatment_fn=fn1,
                            parameters={
                                'param1': 1
                            },
                            run_constraints={
                                'minimum_time_interval': 5
                            }
                        ),
                        Treatment(
                            treatment_fn=fn2
                        )
                    ]
                ),
                Event(
                    time_points=[3, 4, 5],
                    treatments=[
                        Sequence([
                            Treatment(
                                treatment_fn=fn1,
                                parameters={
                                    'param1': 1
                                },
                                run_constraints={
                                    'minimum_time_interval': 5
                                }
                            ),
                            Treatment(
                                treatment_fn=fn2
                            )
                        ])
                    ]
                )
            ]
        }
        result = SimConfiguration(operation_lookup=operation_lookup, **config)
        self.assertListEqual([1, 2, 3, 4, 5], result.time_points)
        self.assertEqual(2, len(result.events))
        self.assertEqual(fn1, result.operation_lookup.get('operation1'))
        self.assertEqual(fn2, result.operation_lookup.get('operation2'))
        self.assertDictEqual(operation_lookup, result.operation_lookup)
        self.assertDictEqual({'operation1': {'minimum_time_interval': 5}}, result.run_constraints)
