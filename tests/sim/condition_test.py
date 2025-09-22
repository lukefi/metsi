import unittest

from lukefi.metsi.sim.condition import Condition


class ConditionTest(unittest.TestCase):
    def test_condition_combinations(self):
        c1 = Condition[int](lambda t, _: t >= 2)
        c2 = Condition[int](lambda _, x: x < 5)

        c_and = c1 & c2
        c_or = c1 | c2

        self.assertTrue(c_and(2, 4))
        self.assertFalse(c_and(1, 4))
        self.assertFalse(c_and(2, 5))
        self.assertFalse(c_and(1, 6))

        self.assertTrue(c_or(3, 4))
        self.assertTrue(c_or(1, 3))
        self.assertTrue(c_or(5, 6))
        self.assertFalse(c_or(1, 6))
