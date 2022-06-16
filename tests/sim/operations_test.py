import unittest
import tests.test_utils
from sim.operations import prepared_operation


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
