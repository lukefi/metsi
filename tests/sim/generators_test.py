import unittest
import sim.generators
import yaml
from sim.core_types import AggregatedResults, Step, OperationPayload, SimConfiguration
from sim.generators import sequence, compose, alternatives, repeat
from sim.runners import evaluate_sequence as run_sequence, evaluate_sequence
from tests.test_utils import inc, dec, aggregating_increment, parametrized_operation


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
        simulation_events:
          - time_points: [0, 1]
            generators:
              - sequence:
                - inc
                - inc
        """
        config = SimConfiguration(operation_lookup={'inc': aggregating_increment}, **yaml.load(declaration, Loader=yaml.CLoader))
        generators = map(lambda x: x.prepared_generator, sim.generators.full_tree_generators(config))
        result = compose(*generators)
        chain = result.operation_chains()[0]
        payload = OperationPayload(
            simulation_state=0,
            aggregated_results=AggregatedResults(),
            operation_history=[]
            )
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(5, len(chain))
        self.assertEqual(4, computation_result.simulation_state)

    def test_operation_run_constraints_success(self):
        declaration = """
        run_constraints:
            inc:
                minimum_time_interval: 2
        simulation_events:
          - time_points: [1, 3]
            generators:
              - sequence:
                - inc
        """
        config = SimConfiguration(operation_lookup={'inc': aggregating_increment}, **yaml.load(declaration, Loader=yaml.CLoader))
        generators = map(lambda x: x.prepared_generator, sim.generators.full_tree_generators(config))
        result = compose(*generators)
        chain = result.operation_chains()[0]
        payload = OperationPayload(
            simulation_state=0,
            aggregated_results=AggregatedResults(),
            operation_history=[]
            )
        computation_result = run_sequence(payload, *chain)
        self.assertEqual(3, len(chain))
        self.assertEqual(2, computation_result.simulation_state)

    def test_operation_run_constraints_fail(self):
        declaration = """
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
        config = SimConfiguration(operation_lookup={'inc': inc}, **yaml.load(declaration, Loader=yaml.CLoader))
        generators = map(lambda x: x.prepared_generator, sim.generators.full_tree_generators(config))
        result = compose(*generators)
        chain = result.operation_chains()[0]
        payload = OperationPayload(simulation_state=0, run_history={}, aggregated_results=AggregatedResults())
        self.assertRaises(Exception, run_sequence, payload, *chain)

    def test_tree_generators_by_time_point(self):
        declaration = """
        simulation_events:
          - time_points: [0, 1]
            generators:
              - sequence:
                - inc
                - inc
        """
        config = SimConfiguration(operation_lookup={'inc': inc}, **yaml.load(declaration, Loader=yaml.CLoader))
        # generators for 2 time points'
        generators = sim.generators.partial_tree_generators_by_time_point(config)
        self.assertEqual(2, len(generators.values()))

        # 1 sequence generators in each time point
        gen_one = list(map(lambda x: x.prepared_generator, generators[0]))
        gen_two = list(map(lambda x: x.prepared_generator, generators[1]))
        self.assertEqual(1, len(gen_one))
        self.assertEqual(1, len(gen_two))

        # 1 chain from both generated trees
        # 1 root + 2 processors (inc) in both chains
        tree_one = compose(*gen_one)
        tree_two = compose(*gen_two)
        chain_one = tree_one.operation_chains()
        chain_two = tree_two.operation_chains()
        self.assertEqual(1, len(chain_one))
        self.assertEqual(1, len(chain_two))
        self.assertEqual(3, len(chain_one[0]))
        self.assertEqual(3, len(chain_two[0]))

    def test_simple_processable_chain(self):
        operation_tags = ['inc', 'inc', 'inc', 'param_oper']
        operation_params = {'param_oper': [{'amplify': True}]}
        operation_lookup = {'inc': inc, 'param_oper': parametrized_operation}
        chain = sim.generators.simple_processable_chain(operation_tags, operation_params, operation_lookup)
        self.assertEqual(len(operation_tags), len(chain))
        result = evaluate_sequence(1, *chain)
        self.assertEqual(4000, result)


    def test_simple_processable_chain_multiparameter_exception(self):
        operation_tags = ['param_oper']
        operation_params = {'param_oper': [{'amplify': True}, {'kissa123': 123}]}
        operation_lookup = {'param_oper': parametrized_operation}
        self.assertRaises(Exception, sim.generators.simple_processable_chain, operation_tags, operation_params, operation_lookup)

    def test_generate_time_series(self):
        declaration = """
        simulation_events:
          - time_points: [0, 1, 4, 100, 1000, 8, 9]
            generators:
              - sequence:
                - inc
                - inc
          - time_points: [9, 8]
            generators:
              - sequence:
                - inc
                - inc
          - time_points: [4, 6, 10, 12]
            generators:
              - sequence:
                - inc
                - inc
        """
        result = SimConfiguration(**yaml.safe_load(declaration))
        self.assertEqual([0, 1, 4, 6, 8, 9, 10, 12, 100, 1000], result.time_points)
