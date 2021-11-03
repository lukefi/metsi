import unittest
from sim.runners import sequence, split
from typing import Optional, Any


def raises(x: Any) -> None:
    raise Exception("Run failure")


def idem(x: Any) -> Any:
    return x


def none(x: Any) -> None:
    return None


def inc(x: int) -> int:
    return x + 1


class TestOperations(unittest.TestCase):
    def test_sequence_success(self):
        input_value = 1
        result = sequence(
            input_value,
            idem,
            none
        )
        self.assertEqual(None, result)

    def test_sequence_failure(self):
        input_value = 1
        prepared_function = lambda: sequence(
            input_value,
            idem,
            raises,
            idem
        )
        self.assertRaises(Exception, prepared_function)

    def test_split_success(self):
        input_value = 1
        result = split(
            input_value,
            raises,
            idem
        )
        self.assertEqual([None, idem(input_value)], result)

    def test_split_failure(self):
        prepared_function = lambda: split(raises, raises)
        self.assertRaises(Exception, prepared_function)

    def test_sequence_and_split_combination_success(self):
        input_value = 1
        result = sequence(
            input_value,
            lambda x: split(
                x,
                idem,
                lambda y: sequence(
                    y,
                    idem,
                    idem
                )
            ),
            idem
        )
        self.assertEqual([1, 1], result)

    def test_sequence_and_split_combination_failure(self):
        input_value = 1
        prepared_function = lambda: sequence(
            input_value,
            idem,
            lambda: split(
                input_value,
                raises
            ),
            idem
        )
        self.assertRaises(Exception, prepared_function)

    def test_sequence_and_split_with_utility_function(self):
        input_value = 1
        prepared_function = lambda: sequence(
            input_value,
            inc,  # 2
            inc,  # 3
            inc,  # 4
            lambda x: split(
                x,  # 4
                inc,  # 5
                inc  # 5
            )
        )
        result = prepared_function()
        self.assertEqual([5, 5], result)
