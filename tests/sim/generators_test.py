import unittest
import sim.generators
import yaml
from sim.core_types import Step, OperationPayload
from sim.generators import sequence, compose, alternatives, repeat
from sim.runners import evaluate_sequence as run_sequence
from tests.test_utils import inc, dec


class TestGenerators(unittest.TestCase):
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

    def test_branch_generating(self):
        parent1 = Step()
        parent2 = Step()
        result = alternatives(
            [parent1, parent2],
            *[inc, inc, inc]
        )
        self.assertEqual(6, len(result))
        self.assertEqual(3, len(parent1.branches))
        self.assertEqual(3, len(parent2.branches))

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

    def test_branches_and_sequences_chainability(self):
        generators = [
            lambda x: sequence(
                x,
                inc,
                inc
            ),
            lambda y: alternatives(
                y,
                inc,
                dec
            ),
            lambda z: sequence(
                z,
                inc,
                inc
            )
        ]
        result = compose(*generators)
        chains = result.operation_chains()
        self.assertEqual(2, len(chains))
        chain1 = chains[0]
        chain2 = chains[1]
        self.assertEqual(6, len(chain1))
        self.assertEqual(6, len(chain2))
        computation_result1 = run_sequence(0, *chain1)
        computation_result2 = run_sequence(0, *chain2)
        self.assertEqual(5, computation_result1)
        self.assertEqual(3, computation_result2)

    def test_repeat(self):
        generators = repeat(
            2,
            lambda x: sequence(
                x,
                inc,
                inc
            ))
        result = compose(*generators)
        chain = result.operation_chains()[0]
        computation_result = run_sequence(0, *chain)
        self.assertEqual(5, len(chain))
        self.assertEqual(4, computation_result)

    def test_yaml_declaration(self):
        declaration = """
        simulation_params:
          initial_step_time: 0
          step_time_interval: 1
          final_step_time: 1
        simulation_events:
          - time_points: [0, 1]
            generators:
              - sequence:
                - inc
                - inc
        """
        generators = sim.generators.full_tree_generators(
            yaml.load(declaration, Loader=yaml.CLoader), {'inc': inc})
        result = compose(*generators)
        chain = result.operation_chains()[0]
        payload = OperationPayload(simulation_state=0, run_history={})
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(5, len(chain))
        self.assertEqual(4, computation_result.simulation_state)

    def test_operation_run_constraints_success(self):
        declaration="""
        simulation_params:
            initial_step_time: 0
            step_time_interval: 1
            final_step_time: 3
        run_constraints:
            inc:
                minimum_time_interval: 2
        simulation_events:
          - time_points: [1, 3]
            generators:
              - sequence:
                - inc
        """
        generators = sim.generators.full_tree_generators(
            yaml.safe_load(declaration), {'inc': inc})
        result = compose(*generators)
        chain = result.operation_chains()[0]
        payload = OperationPayload(simulation_state=0, run_history={})
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(3, len(chain))
        self.assertEqual(2, computation_result.simulation_state)

    def test_operation_run_constraints_fail(self):
        declaration="""
        simulation_params:
            initial_step_time: 0
            step_time_interval: 1
            final_step_time: 3
        run_constraints:
            inc:
                minimum_time_interval: 2
        simulation_events:
          - time_points: [1, 3]
            generators:
              - sequence:
                - inc
                - inc
        """
        generators = sim.generators.full_tree_generators(
            yaml.safe_load(declaration), {'inc': inc})
        result = compose(*generators)
        chain = result.operation_chains()[0]
        payload = OperationPayload(simulation_state=0, run_history={})
        self.assertRaises(Exception, run_sequence, payload, *chain)

    def test_tree_generators_by_time_point(self):
        declaration = """
        simulation_params:
          initial_step_time: 0
          step_time_interval: 1
          final_step_time: 1
        simulation_events:
          - time_points: [0, 1]
            generators:
              - sequence:
                - inc
                - inc
        """

        # generators for 2 time points'
        generators = sim.generators.partial_tree_generators_by_time_point(yaml.safe_load(declaration), {'inc': inc})
        self.assertEqual(2, len(generators.values()))

        # 1 sequence generators in each time point
        gen_one = generators[0]
        gen_two = generators[1]
        self.assertEqual(1, len(gen_one))
        self.assertEqual(1, len(gen_two))

        # 1 chain from both generated trees
        # 1 root + 2 processors (inc) in both chains
        tree_one = compose(*generators[0])
        tree_two = compose(*generators[1])
        chain_one = tree_one.operation_chains()
        chain_two = tree_two.operation_chains()
        self.assertEqual(1, len(chain_one))
        self.assertEqual(1, len(chain_two))
        self.assertEqual(3, len(chain_one[0]))
        self.assertEqual(3, len(chain_two[0]))
