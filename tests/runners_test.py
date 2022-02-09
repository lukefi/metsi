import unittest
from sim.runners import evaluate_sequence

from test_utils import raises, identity, none


class TestOperations(unittest.TestCase):
    def test_sequence_success(self):
        input_value = 1
        result = evaluate_sequence(
            input_value,
            identity,
            none
        )
        self.assertEqual(None, result)

    def test_sequence_failure(self):
        input_value = 1
        prepared_function = lambda: evaluate_sequence(
            input_value,
            identity,
            raises,
            identity
        )
        self.assertRaises(Exception, prepared_function)
