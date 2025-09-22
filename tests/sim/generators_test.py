from typing import Callable
import unittest
from lukefi.metsi.domain.conditions import MinimumTimeInterval
from lukefi.metsi.sim.collected_data import CollectedData
from lukefi.metsi.sim.operations import simple_processable_chain
from lukefi.metsi.sim.simulation_instruction import SimulationInstruction
from lukefi.metsi.sim.generators import Alternatives, Sequence, Event
from lukefi.metsi.sim.simulation_payload import SimulationPayload
from lukefi.metsi.sim.runners import evaluate_sequence as run_sequence, evaluate_sequence
from lukefi.metsi.sim.sim_configuration import SimConfiguration
from tests.test_utils import inc, collecting_increment, parametrized_operation


class TestGenerators(unittest.TestCase):
    def test_yaml_declaration(self):
        declaration = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0, 1],
                    events=Sequence([
                        Event(
                            treatment=collecting_increment
                        ),
                        Event(
                            treatment=collecting_increment
                        ),
                    ])
                )
            ]
        }
        config = SimConfiguration(**declaration)
        generator = config.full_tree_generators()
        result = generator.compose_nested()
        chain = result.operation_chains()[0]
        payload = SimulationPayload(
            computational_unit=0,
            collected_data=CollectedData(),
            operation_history=[]
        )
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(5, len(chain))
        self.assertEqual(4, computation_result.computational_unit)

    def test_operation_run_constraints_success(self):
        declaration = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[1, 3],
                    events=Sequence([
                        Event(
                            preconditions=[
                                MinimumTimeInterval(2, collecting_increment)
                            ],
                            treatment=collecting_increment
                        )
                    ])
                )
            ]
        }
        config = SimConfiguration(**declaration)
        generator = config.full_tree_generators()
        result = generator.compose_nested()
        chain = result.operation_chains()[0]
        payload = SimulationPayload(
            computational_unit=0,
            collected_data=CollectedData(),
            operation_history=[]
        )
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(3, len(chain))
        self.assertEqual(2, computation_result.computational_unit)

    def test_operation_run_constraints_fail(self):
        declaration = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[1, 3],
                    events=Sequence([
                        Event(
                            preconditions=[
                                MinimumTimeInterval(2, inc)
                            ],
                            treatment=inc
                        ),
                        Event(
                            preconditions=[
                                MinimumTimeInterval(2, inc)
                            ],
                            treatment=inc
                        )
                    ])
                )
            ]
        }
        config = SimConfiguration(**declaration)
        generator = config.full_tree_generators()
        result = generator.compose_nested()
        chain = result.operation_chains()[0]
        payload = SimulationPayload(computational_unit=0,
                                   operation_history=[],
                                   collected_data=CollectedData())
        self.assertRaises(Exception, run_sequence, payload, *chain)

    def test_tree_generators_by_time_point(self):
        declaration = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0, 1],
                    events=Sequence([
                        Event(
                            inc
                        ),
                        Event(
                            inc
                        )
                    ])
                )
            ]
        }
        config = SimConfiguration(**declaration)
        # generators for 2 time points'
        generators = config.partial_tree_generators_by_time_point()
        self.assertEqual(2, len(generators.values()))

        # 1 sequence generators in each time point
        gen_one = generators[0]
        gen_two = generators[1]

        # 1 chain from both generated trees
        # 1 root + 2 processors (inc) in both chains
        tree_one = gen_one.compose_nested()
        tree_two = gen_two.compose_nested()
        chain_one = tree_one.operation_chains()
        chain_two = tree_two.operation_chains()
        self.assertEqual(1, len(chain_one))
        self.assertEqual(1, len(chain_two))
        self.assertEqual(3, len(chain_one[0]))
        self.assertEqual(3, len(chain_two[0]))

    def test_nested_tree_generators(self):
        """Create a nested generators event tree. Use simple incrementation operation with starting value 0. Sequences
        and alternatives result in 4 branches with separately incremented values."""
        declaration = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0],
                    events=Sequence([
                        Event(collecting_increment),
                        Sequence([
                            Event(collecting_increment)
                        ]),
                        Alternatives([
                            Event(collecting_increment),
                            Sequence([
                                Event(collecting_increment),
                                Alternatives([
                                    Event(collecting_increment),
                                    Sequence([
                                        Event(collecting_increment),
                                        Event(collecting_increment)
                                    ])
                                ])
                            ]),
                            Sequence([
                                Event(collecting_increment),
                                Event(collecting_increment),
                                Event(collecting_increment),
                                Event(collecting_increment)
                            ])
                        ]),
                        Event(collecting_increment),
                        Event(collecting_increment)
                    ])
                )
            ]
        }
        config = SimConfiguration(**declaration)
        generator = config.full_tree_generators()
        tree = generator.compose_nested()
        chains = tree.operation_chains()
        self.assertEqual(4, len(chains))

        lengths = []
        results = []

        for chain in chains:
            value = evaluate_sequence(
                SimulationPayload(
                    computational_unit=0,
                    operation_history=[],
                    collected_data=CollectedData()),
                *chain
            ).computational_unit
            results.append(value)
            lengths.append(len(chain))

        # chain lengths have the root no_op function at start
        self.assertListEqual([6, 7, 8, 9], lengths)
        self.assertListEqual([5, 6, 7, 8], results)

    def test_nested_tree_generators_multiparameter_alternative(self):
        def increment(x, **y):
            return collecting_increment(x, **y)

        def inc_param(x, **y):
            return collecting_increment(x, **y)

        declaration = {
            "operation_params": {
                inc_param: [
                    {"incrementation": 2},
                    {"incrementation": 3}
                ]
            },
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0],
                    events=Sequence([
                        Event(increment),
                        Alternatives([
                            Sequence([
                                Event(increment)
                            ]),
                            Alternatives([
                                Event(
                                    inc_param,
                                    parameters={
                                        "incrementation": 2
                                    }
                                ),
                                Event(
                                    inc_param,
                                    parameters={
                                        "incrementation": 3
                                    }
                                )

                            ]),
                        ]),
                        Event(increment)
                    ])
                )
            ]
        }
        config = SimConfiguration(**declaration)
        generator = config.full_tree_generators()
        tree = generator.compose_nested()
        chains = tree.operation_chains()
        self.assertEqual(3, len(chains))

        lengths = []
        results = []

        for chain in chains:
            value = evaluate_sequence(
                SimulationPayload(
                    computational_unit=0,
                    operation_history=[],
                    collected_data=CollectedData()),
                *chain
            ).computational_unit
            results.append(value)
            lengths.append(len(chain))

        self.assertListEqual([3, 4, 5], results)

    def test_alternatives_embedding_equivalence(self):
        """
        This test shows that alternatives with multiple single operations nested in alternatives is equivalent to
        sequences with single operations nested in alternatives.
        """
        declaration_one = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0],
                    events=Sequence([
                        Event(collecting_increment),
                        Alternatives([
                            Alternatives([
                                Event(collecting_increment),
                                Event(collecting_increment)
                            ]),
                            Sequence([
                                Event(collecting_increment),
                                Event(collecting_increment)
                            ]),
                            Alternatives([
                                Event(collecting_increment),
                                Event(collecting_increment)
                            ])
                        ]),
                        Event(collecting_increment)
                    ])
                )
            ]
        }
        declaration_two = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0],
                    events=Sequence([
                        Event(collecting_increment),
                        Alternatives([
                            Sequence([Event(collecting_increment)]),
                            Sequence([Event(collecting_increment)]),
                            Sequence([Event(collecting_increment), Event(collecting_increment)]),
                            Sequence([Event(collecting_increment)]),
                            Sequence([Event(collecting_increment)])
                        ]),
                        Event(collecting_increment)
                    ])
                )
            ]
        }
        configs = [
            SimConfiguration(**declaration_one),
            SimConfiguration(**declaration_two)
        ]
        generators = [config.full_tree_generators() for config in configs]
        trees = [generator.compose_nested() for generator in generators]
        chains_sets = [tree.operation_chains() for tree in trees]

        results = ([], [])
        for i, chains in enumerate(chains_sets):
            for chain in chains:
                value = evaluate_sequence(
                    SimulationPayload(
                        computational_unit=0,
                        operation_history=[],
                        collected_data=CollectedData()),
                    *chain
                ).computational_unit
                results[i].append(value)
        self.assertListEqual(results[0], results[1])

    def test_simple_processable_chain(self):
        operation_tags: list[Callable] = [inc, inc, inc, parametrized_operation]
        operation_params = {parametrized_operation: [{'amplify': True}]}
        chain = simple_processable_chain(operation_tags,
                                                                     operation_params)
        self.assertEqual(len(operation_tags), len(chain))
        result = evaluate_sequence(SimulationPayload(computational_unit=1,
                                                    collected_data=None,
                                                    operation_history={}), *chain)
        self.assertEqual(4000, result.computational_unit)

    def test_simple_processable_chain_multiparameter_exception(self):
        operation_tags = ['param_oper']
        operation_params = {'param_oper': [{'amplify': True}, {'kissa123': 123}]}
        operation_lookup = {'param_oper': parametrized_operation}
        self.assertRaises(Exception,
                          simple_processable_chain,
                          operation_tags,
                          operation_params,
                          operation_lookup)

    def test_generate_time_series(self):
        declaration = {
            "simulation_events": [
                SimulationInstruction(
                    time_points=[0, 1, 4, 100, 1000, 8, 9],
                    events=Sequence([
                        Event(inc),
                        Event(inc)
                    ])
                ),
                SimulationInstruction(
                    time_points=[9, 8],
                    events=Sequence([
                        Event(inc),
                        Event(inc)
                    ])
                ),
                SimulationInstruction(
                    time_points=[4, 6, 10, 12],
                    events=Sequence([
                        Event(inc),
                        Event(inc)
                    ])
                )
            ]
        }
        result = SimConfiguration(**declaration)
        self.assertEqual([0, 1, 4, 6, 8, 9, 10, 12, 100, 1000], result.time_points)
