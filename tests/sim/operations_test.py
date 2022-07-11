import unittest
from sim.util import merge_operation_params, read_operation_file_params
import tests.test_utils
from sim.operations import prepared_operation, prepared_processor


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
        read_file_params = read_operation_file_params("dummy_operation", file_params)
        merged_params = merge_operation_params(operation_params, read_file_params)
        operation = prepared_operation(
            tests.test_utils.parametrized_operation_using_file_parameter, 
            **merged_params
        )

        self.assertEqual(operation("foo"), "kissa123\n")

