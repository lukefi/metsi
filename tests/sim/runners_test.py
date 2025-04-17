import unittest
from lukefi.metsi.sim.generators import GENERATOR_LOOKUP
from lukefi.metsi.sim.core_types import CollectedData, OperationPayload, SimConfiguration
from lukefi.metsi.sim.runners import evaluate_sequence, run_full_tree_strategy, run_partial_tree_strategy, \
    chain_evaluator, depth_first_evaluator
from tests.test_utils import raises, identity, none, collect_results, collecting_increment
from lukefi.metsi.app.file_io import read_control_module

class RunnersTest(unittest.TestCase):
    def test_sequence_success(self):
        payload = OperationPayload(computational_unit=1)
        result = evaluate_sequence(
            payload,
            identity,
            none
        )
        self.assertEqual(None, result)

    def test_sequence_failure(self):
        payload = OperationPayload(computational_unit=1)
        prepared_function = lambda: evaluate_sequence(
            payload,
            identity,
            raises,
            identity
        )
        self.assertRaises(Exception, prepared_function)

    def test_event_tree_formation_strategies_by_comparison(self):
        declaration = read_control_module('tests\\resources\\runners_test\\branching.py')
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=GENERATOR_LOOKUP,
                                  **declaration)
        print(config)
        initial = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )
        results_full = collect_results(run_full_tree_strategy(initial, config))
        results_partial = collect_results(run_partial_tree_strategy(initial, config))
        self.assertEqual(8, len(results_full))
        self.assertEqual(8, len(results_partial))
        self.assertEqual(results_partial, results_full)

    def test_full_formation_evaluation_strategies_by_comparison(self):
        declaration = read_control_module('tests\\resources\\runners_test\\branching.py')
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=GENERATOR_LOOKUP,
                                  **declaration)
        print(config)
        chains_payload = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )
        results_chains = collect_results(run_full_tree_strategy(chains_payload, config, chain_evaluator))

        depth_payload = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )
        results_depth = collect_results(run_full_tree_strategy(depth_payload, config, depth_first_evaluator))
        self.assertEqual(8, len(results_chains))
        self.assertEqual(8, len(results_depth))
        self.assertEqual(results_chains, results_depth)

    def test_partial_formation_evaluation_strategies_by_comparison(self):
        declaration = read_control_module('tests\\resources\\runners_test\\branching.py')
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=GENERATOR_LOOKUP,
                                  **declaration)
        print(config)
        chains_payload = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )
        results_chains = collect_results(run_partial_tree_strategy(chains_payload, config, chain_evaluator))

        depth_payload = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )
        results_depth = collect_results(run_partial_tree_strategy(depth_payload, config, depth_first_evaluator))
        self.assertEqual(8, len(results_chains))
        self.assertEqual(8, len(results_depth))
        self.assertEqual(results_chains, results_depth)

    def test_no_parameters_propagation(self):
        declaration = read_control_module('tests\\resources\\runners_test\\no_parameters.py')
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=GENERATOR_LOOKUP,
                                  **declaration)
        # print(config)
        initial = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )

        results = collect_results(
            run_full_tree_strategy(initial, config)
        )
        self.assertEqual(5, results[0])

    def test_parameters_propagation(self):
        declaration = read_control_module('tests\\resources\\runners_test\\parameters.py')
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=GENERATOR_LOOKUP,
                                  **declaration)
        # print(config)
        initial = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )

        results = collect_results(
            run_full_tree_strategy(initial, config)
        )
        self.assertEqual(9, results[0])

    def test_parameters_branching(self):
        declaration = read_control_module('tests\\resources\\runners_test\\parameters_branching.py')
        config = SimConfiguration(operation_lookup={'inc': collecting_increment},
                                  generator_lookup=GENERATOR_LOOKUP,
                                  **declaration)
        initial = OperationPayload(
            computational_unit=1,
            collected_data=CollectedData(),
            operation_history=[]
        )

        results = collect_results(
            run_full_tree_strategy(initial, config)
        )
        # do_nothing, do_nothing = 1
        # do_nothing, inc#1      = 2
        # do_nothing, inc#2      = 3
        # inc#1, do_nothing      = 2
        # inc#1, inc#1           = 3
        # inc#1, inc#2           = 4
        # inc#2, do_nothing      = 3
        # inc#2, inc#1           = 4
        # inc#2, inc#2           = 5
        expected = [1, 2, 3, 2, 3, 4, 3, 4, 5]
        self.assertEqual(expected, results)
