import unittest
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.sim.operation_payload import OperationPayload
import tests.test_utils
from lukefi.metsi.domain.conditions import _get_operation_last_run
from lukefi.metsi.sim.operations import prepared_operation


class SimOperationsTest(unittest.TestCase):
    def test_prepared_operation(self):
        assertions = [
            ([10, {}], 10),
            ([10, {'amplify': True}], 10000),
            ([10, {'amplify': False}], 10)
        ]

        for case in assertions:
            function = prepared_operation(tests.test_utils.parametrized_operation, **case[0][1])
            result = function(OperationPayload(computational_unit=case[0][0],
                                               collected_data=None,
                                               operation_history={}))
            self.assertEqual(case[1], result.computational_unit)

    def test_operation_last_run(self):

        def operation1(x: OpTuple) -> OpTuple:
            return x

        def operation2(x: OpTuple) -> OpTuple:
            return x

        def operation3(x: OpTuple) -> OpTuple:
            return x

        def operation4(x: OpTuple) -> OpTuple:
            return x

        operation_history = [
            (1, operation1, {}),
            (2, operation2, {}),
            (3, operation1, {}),
            (4, operation3, {}),
            (5, operation1, {}),
            (6, operation2, {}),
            (7, operation1, {}),
            (8, operation3, {}),
            (9, operation1, {})
        ]

        self.assertEqual(_get_operation_last_run(operation_history, operation1), 9)
        self.assertEqual(_get_operation_last_run(operation_history, operation2), 6)
        self.assertEqual(_get_operation_last_run(operation_history, operation3), 8)
        self.assertEqual(_get_operation_last_run(operation_history, operation4), None)
