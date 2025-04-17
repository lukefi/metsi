import unittest
import lukefi.metsi.sim.generators
from lukefi.metsi.sim.core_types import CollectedData, EventTree, OperationPayload, SimConfiguration
from lukefi.metsi.sim.generators import sequence, compose_nested, alternatives
from lukefi.metsi.sim.runners import evaluate_sequence as run_sequence, evaluate_sequence
from tests.test_utils import inc, collecting_increment, parametrized_operation


class TestGenerators(unittest.TestCase):
    def test_event_sequence_generating(self):
        root = EventTree()
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

    def test_branch_generating(self):
        parent1 = EventTree()
        parent2 = EventTree()
        result = alternatives(
            [parent1, parent2],
            *[inc, inc, inc]
        )
        self.assertEqual(6, len(result))
        self.assertEqual(3, len(parent1.branches))
        self.assertEqual(3, len(parent2.branches))

    def test_yaml_declaration(self):
        declaration = {
            "simulation_events": [
          {
              "time_points": [0, 1],
              "generators": [
            {
                "sequence": [
              "inc",
              "inc"
                ]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                                  **declaration)
        generator = lukefi.metsi.sim.generators.full_tree_generators(config)
        result = compose_nested(generator)
        chain = result.operation_chains()[0]
        payload = OperationPayload(
            computational_unit=0,
            collected_data=CollectedData(),
            operation_history=[]
            )
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(5, len(chain))
        self.assertEqual(4, computation_result.computational_unit)

    def test_operation_run_constraints_success(self):
        declaration = {
            "run_constraints": {
          "inc": {
              "minimum_time_interval": 2
          }
            },
            "simulation_events": [
          {
              "time_points": [1, 3],
              "generators": [
            {
                "sequence": ["inc"]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                                  **declaration)
        generator = lukefi.metsi.sim.generators.full_tree_generators(config)
        result = compose_nested(generator)
        chain = result.operation_chains()[0]
        payload = OperationPayload(
            computational_unit=0,
            collected_data=CollectedData(),
            operation_history=[]
            )
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(3, len(chain))
        self.assertEqual(2, computation_result.computational_unit)

    def test_operation_run_constraints_fail(self):
        declaration = {
            "run_constraints": {
          "inc": {
              "minimum_time_interval": 2
          }
            },
            "simulation_events": [
          {
              "time_points": [1, 3],
              "generators": [
            {
                "sequence": [
              "inc",
              "inc"
                ]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={'inc': inc},
                                  generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                                  **declaration)
        generator = lukefi.metsi.sim.generators.full_tree_generators(config)
        result = compose_nested(generator)
        chain = result.operation_chains()[0]
        payload = OperationPayload(computational_unit=0,
                                   operation_history=[],
                                   collected_data=CollectedData())
        self.assertRaises(Exception, run_sequence, payload, *chain)

    def test_tree_generators_by_time_point(self):
        declaration = {
            "simulation_events": [
          {
              "time_points": [0, 1],
              "generators": [
            {
                "sequence": [
              "inc",
              "inc"
                ]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={'inc': inc},
                                  generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                                  **declaration)
        # generators for 2 time points'
        generators = lukefi.metsi.sim.generators.partial_tree_generators_by_time_point(config)
        self.assertEqual(2, len(generators.values()))

        # 1 sequence generators in each time point
        gen_one = generators[0]
        gen_two = generators[1]

        # 1 chain from both generated trees
        # 1 root + 2 processors (inc) in both chains
        tree_one = compose_nested(gen_one)
        tree_two = compose_nested(gen_two)
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
          {
              "time_points": [0],
              "generators": [
            {
                "sequence": [
              "inc",  # 1
              {
                  "sequence": [
                "inc"  # 2
                  ]
              },
              {
                  "alternatives": [
                "inc",  # 3
                {
                    "sequence": [
                  "inc",  # 3
                  {
                      "alternatives": [
                    "inc",  # 4
                    {
                        "sequence": [
                      "inc",  # 4
                      "inc"  # 5
                        ]
                    }
                      ]
                  }
                    ]
                },
                {
                    "sequence": [
                  "inc",  # 3
                  "inc",  # 4
                  "inc",  # 5
                  "inc"  # 6
                    ]
                }
                  ]
              },
              "inc",  # 4, 5, 6, 7
              "inc"  # 5, 6, 7, 8
                ]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                                  **declaration)
        generator = lukefi.metsi.sim.generators.full_tree_generators(config)
        tree = compose_nested(generator)
        chains = tree.operation_chains()
        self.assertEqual(4, len(chains))

        lengths = []
        results = []

        for chain in chains:
            value = evaluate_sequence(
                OperationPayload(
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
        declaration = {
            "operation_params": {
          "inc_param": [
              {"incrementation": 2},
              {"incrementation": 3}
          ]
            },
            "simulation_events": [
          {
              "time_points": [0],
              "generators": [
            {
                "sequence": [
              "inc",
              {
                  "alternatives": [
                {
                    "sequence": ["inc"]
                },
                "inc_param"
                  ]
              },
              "inc"
                ]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={
              'inc_param': collecting_increment,
              'inc': collecting_increment
            },
            generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
            **declaration)
        generator = lukefi.metsi.sim.generators.full_tree_generators(config)
        tree = compose_nested(generator)
        chains = tree.operation_chains()
        self.assertEqual(3, len(chains))

        lengths = []
        results = []

        for chain in chains:
            value = evaluate_sequence(
                OperationPayload(
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
          {
              "time_points": [0],
              "generators": [
            {
                "sequence": [
              "inc",
              {
                  "alternatives": [
                {
                    "alternatives": [
                  "inc",
                  "inc"
                    ]
                },
                {
                    "sequence": [
                  "inc",
                  "inc"
                    ]
                },
                {
                    "alternatives": [
                  "inc",
                  "inc"
                    ]
                }
                  ]
              },
              "inc"
                ]
            }
              ]
          }
            ]
        }
        declaration_two = {
            "simulation_events": [
          {
              "time_points": [0],
              "generators": [
            {
                "sequence": [
              "inc",
              {
                  "alternatives": [
                {"sequence": ["inc"]},
                {"sequence": ["inc"]},
                {"sequence": ["inc", "inc"]},
                {"sequence": ["inc"]},
                {"sequence": ["inc"]}
                  ]
              },
              "inc"
                ]
            }
              ]
          }
            ]
        }
        configs = [
            SimConfiguration(operation_lookup={'inc_param': collecting_increment,
                                               'inc': collecting_increment},
                             generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                             **declaration_one),
            SimConfiguration(operation_lookup={'inc_param': collecting_increment,
                                               'inc': collecting_increment},
                             generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                             **declaration_two)
        ]
        generators = [ lukefi.metsi.sim.generators.full_tree_generators(config) for config in configs ]
        trees = [ compose_nested(generator) for generator in generators ]
        chains_sets = [ tree.operation_chains() for tree in trees ]

        results = ([], [])
        for i, chains in enumerate(chains_sets):
            for chain in chains:
                value = evaluate_sequence(
                    OperationPayload(
                        computational_unit=0,
                        operation_history=[],
                        collected_data=CollectedData()),
                    *chain
                ).computational_unit
                results[i].append(value)
        self.assertListEqual(results[0], results[1])

    def test_simulation_events_sequence_multiparameter_exception(self):
        declaration = {
            "operation_params": {
          "inc": [
              {"param1": 1},
              {"param1": 2}
          ]
            },
            "simulation_events": [
          {
              "time_points": [0],
              "generators": [
            {
                "sequence": [
              "inc"
                ]
            }
              ]
          }
            ]
        }
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
                                  **declaration)
        self.assertRaises(Exception, lukefi.metsi.sim.generators.full_tree_generators, config)

    def test_simple_processable_chain(self):
        operation_tags = ['inc', 'inc', 'inc', 'param_oper']
        operation_params = {'param_oper': [{'amplify': True}]}
        operation_lookup = {'inc': inc, 'param_oper': parametrized_operation}
        chain = lukefi.metsi.sim.generators.simple_processable_chain(operation_tags,
                                                                     operation_params,
                                                                     operation_lookup)
        self.assertEqual(len(operation_tags), len(chain))
        result = evaluate_sequence(1, *chain)
        self.assertEqual(4000, result)

    def test_simple_processable_chain_multiparameter_exception(self):
        operation_tags = ['param_oper']
        operation_params = {'param_oper': [{'amplify': True}, {'kissa123': 123}]}
        operation_lookup = {'param_oper': parametrized_operation}
        self.assertRaises(Exception,
                          lukefi.metsi.sim.generators.simple_processable_chain,
                          operation_tags,
                          operation_params,
                          operation_lookup)

    def test_generate_time_series(self):
        declaration = {
            "simulation_events": [
          {
              "time_points": [0, 1, 4, 100, 1000, 8, 9],
              "generators": [
            {
                "sequence": [
              "inc",
              "inc"
                ]
            }
              ]
          },
          {
              "time_points": [9, 8],
              "generators": [
            {
                "sequence": [
              "inc",
              "inc"
                ]
            }
              ]
          },
          {
              "time_points": [4, 6, 10, 12],
              "generators": [
            {
                "sequence": [
              "inc",
              "inc"
                ]
            }
              ]
          }
            ]
        }
        dummy_dict = {}
        result = SimConfiguration(dummy_dict,
                                  dummy_dict,
                                  **declaration)
        self.assertEqual([0, 1, 4, 6, 8, 9, 10, 12, 100, 1000], result.time_points)
