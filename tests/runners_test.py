import unittest
from sim.runners import sequence, split


def raises():
    raise Exception("Run failure")


def one():
    return 1


def none():
    return None


class TestOperations(unittest.TestCase):
    def test_sequence_success(self):
        result = sequence(
            one,
            none
        )
        self.assertEqual([one(), none()], result)

    def test_sequence_failure(self):
        prepared_function = lambda: sequence(
            one,
            raises,
            one
        )
        self.assertRaises(Exception, prepared_function)

    def test_split_success(self):
        result = split(
            raises,
            one
        )
        self.assertEqual([None, one()], result)

    def test_split_failure(self):
        prepared_function = lambda: split(raises, raises)
        self.assertRaises(Exception, prepared_function)

    def test_sequence_and_split_combination_success(self):
        result = sequence(
            lambda: split(
                one,
                lambda: sequence(
                    one,
                    one
                )
            ),
            one
        )
        self.assertEqual([[one(), [one(), one()]], one()], result)

    def test_sequence_and_split_combination_failure(self):
        prepared_function = lambda: sequence(
            one,
            lambda: split(
                raises
            ),
            one
        )
        self.assertRaises(Exception, prepared_function)
