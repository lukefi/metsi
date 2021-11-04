import unittest
from sim.runners import sequence, alternatives, follow
from typing import Any


def raises(x: Any) -> None:
    raise Exception("Run failure")


def idem(x: Any) -> Any:
    return x


def none(x: Any) -> None:
    return None


def inc(x: int) -> int:
    return x + 1


def dec(x: int) -> int:
    return x - 1


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

    def test_alternatives_success(self):
        input_value = 1
        result = alternatives(
            input_value,
            raises,
            idem
        )
        self.assertEqual([None, idem(input_value)], result)

    def test_alternatives_failure(self):
        prepared_function = lambda: alternatives(raises, raises)
        self.assertRaises(Exception, prepared_function)

    def test_sequence_and_alternatives_combination_success(self):
        input_value = 1
        result = sequence(
            input_value,
            lambda x: alternatives(
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

    def test_sequence_and_alternatives_combination_failure(self):
        input_value = 1
        prepared_function = lambda: sequence(
            input_value,
            idem,
            lambda: alternatives(
                input_value,
                raises
            ),
            idem
        )
        self.assertRaises(Exception, prepared_function)

    def test_sequence_and_alternatives_with_utility_function(self):
        input_value = 1
        prepared_function = lambda: sequence(
            input_value,
            inc,  # 2
            inc,  # 3
            inc,  # 4
            lambda x: alternatives(
                x,  # 4
                inc,  # 5
                inc  # 5
            )
        )
        result = prepared_function()
        self.assertEqual([5, 5], result)

    def test_follow_failure(self):
        input_values = [10, 20, 30]
        prepared_function = lambda: follow(
            input_values,
            raises
        )
        self.assertRaises(Exception, prepared_function)

    def test_follow_success(self):
        input_values = [10, 20, 30]
        prepared_function = lambda x: follow(
            x,  # [10, 20, 30]
            lambda y: sequence(
                y,  # 10 || 20 || 30
                inc,  # 11 || 21 || 31
                inc,  # 12 || 22 || 32
                lambda z: alternatives(
                    z,  # 12 || 22 || 32
                    inc,  # 13 || 23 || 33
                    dec  # 11 || 21 || 31
                ),
                idem  # [13, 11] || [23, 21] || [33,31]
            )
        )  # --> [[13, 11], [23, 21], [33, 31]]
        result = prepared_function(input_values)
        self.assertEqual([[13, 11], [23, 21], [33, 31]], result)
