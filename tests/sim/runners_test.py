import unittest
from sim.core_types import OperationPayload
from sim.runners import evaluate_sequence, run_full_tree_strategy, run_partial_tree_strategy
from tests.test_utils import raises, identity, none, collect_results, load_yaml, aggregating_increment


class TestOperations(unittest.TestCase):
    def test_sequence_success(self):
        payload = OperationPayload(simulation_state=1)
        result = evaluate_sequence(
            payload,
            identity,
            none
        )
        self.assertEqual(None, result)

    def test_sequence_failure(self):
        payload = OperationPayload(simulation_state=1)
        prepared_function = lambda: evaluate_sequence(
            payload,
            identity,
            raises,
            identity
        )
        self.assertRaises(Exception, prepared_function)

    def test_strategies_by_comparison(self):
        declaration = load_yaml('branching.yaml')
        initial = OperationPayload(
            simulation_state=1,
            run_history={},
            aggregated_results={'operation_results': {}}
        )
        results_full = collect_results(
            run_full_tree_strategy(initial, declaration, {'inc': aggregating_increment}))
        results_partial = collect_results(
            run_partial_tree_strategy(initial, declaration, {'inc': aggregating_increment}))
        self.assertEqual(8, len(results_full))
        self.assertEqual(8, len(results_partial))
        self.assertEqual(results_partial, results_full)

    def test_no_parameters_propagation(self):
        declaration = load_yaml('no_parameters.yaml')
        initial = OperationPayload(
            simulation_state=1,
            run_history={},
            aggregated_results={'operation_results': {}}
        )

        results = collect_results(
            run_full_tree_strategy(initial, declaration, {'inc': aggregating_increment})
        )
        self.assertEqual(5, results[0])

    def test_parameters_propagation(self):
        declaration = load_yaml('parameters.yaml')
        initial = OperationPayload(
            simulation_state=1,
            run_history={},
            aggregated_results={'operation_results': {}}
        )

        results = collect_results(
            run_full_tree_strategy(initial, declaration, {'inc': aggregating_increment})
        )
        self.assertEqual(9, results[0])
