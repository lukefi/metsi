import unittest
from sim.util import merge_operation_params, get_operation_file_params
import tests.test_utils
from sim.operations import prepared_operation, _get_operation_last_run


class OperationsTest(unittest.TestCase):
    def test_prepared_operation(self):
        assertions = [
            ([10, {}], 10),
            ([10, {'amplify': True}], 10000),
            ([10, {'amplify': False}], 10)
        ]

        for case in assertions:
            function = prepared_operation(tests.test_utils.parametrized_operation, **case[0][1])
            result = function(case[0][0])
            self.assertEqual(case[1], result)

    def test_operation_with_params_from_file(self):
        operation_params = {"one": 1, "two": 2}
        file_params = {"dummy_operation": {"dummy_file":"tests/resources/test_dummy"}}
        read_file_params = get_operation_file_params("dummy_operation", file_params)
        merged_params = merge_operation_params(operation_params, read_file_params)
        operation = prepared_operation(
            tests.test_utils.parametrized_operation_using_file_parameter, 
            **merged_params
        )

        self.assertEqual(operation("foo"), "kissa123\n")

    def test_operation_last_run(self):
        operation_history = [
            (1, "operation1", {}),
            (2, "operation2", {}),
            (3, "operation1", {}),
            (4, "operation3", {}),
            (5, "operation1", {}),
            (6, "operation2", {}),
            (7, "operation1", {}),
            (8, "operation3", {}),
            (9, "operation1", {})
        ]

        self.assertEqual(_get_operation_last_run(operation_history, "operation1"), 9)
        self.assertEqual(_get_operation_last_run(operation_history, "operation2"), 6)
        self.assertEqual(_get_operation_last_run(operation_history, "operation3"), 8)
        self.assertEqual(_get_operation_last_run(operation_history, "operationX"), None)


