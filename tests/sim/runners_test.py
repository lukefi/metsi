import unittest

from sim.core_types import OperationPayload
from sim.runners import evaluate_sequence

from tests.test_utils import raises, identity, none


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
