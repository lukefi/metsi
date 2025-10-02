import unittest

from lukefi.metsi.sim.collected_data import CollectedData, OpTuple
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.generators import Alternatives, Sequence, Event
from lukefi.metsi.sim.simulation_payload import SimulationPayload


class ConditionTest(unittest.TestCase):
    def test_condition_combinations(self):

        @Condition[int]
        def c2(time: int, x: int) -> bool:
            _ = time
            return x < 5

        c1 = Condition[int](lambda t, _: t >= 2)

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

    def test_condition_checking(self):
        def step(x: OpTuple[int]) -> OpTuple[int]:
            computational_unit, collected_data = x
            computational_unit = computational_unit.__add__(1)
            return computational_unit, collected_data

        generator = Alternatives([
            Sequence([
                Event(step, preconditions=[Condition(lambda _, x: x.computational_unit.__le__(2))]),
                Event(step, preconditions=[Condition(lambda _, x: x.computational_unit.__ge__(2))]),
                Event(step, postconditions=[Condition(lambda _, x: x.computational_unit.__eq__(4))]),
            ]),
            Sequence([
                Event(step, preconditions=[Condition(lambda _, x: x.computational_unit.__lt__(2))]),
                Event(step, preconditions=[Condition(lambda _, x: x.computational_unit.__ge__(2))]),
                Event(step, postconditions=[Condition(lambda _, x: x.computational_unit.__eq__(3))]),
            ]),
            Sequence([
                Event(step, postconditions=[Condition(lambda _, x: x.computational_unit.__eq__(2))]),
                Event(step, postconditions=[Condition(lambda _, x: x.computational_unit.__lt__(5))]),
            ]),
            Event(step, preconditions=[Condition(lambda _, x: True)]),
            Event(step, preconditions=[Condition(lambda _, x: False)]),
            Event(step, postconditions=[Condition(lambda _, x: True)]),
            Event(step, postconditions=[Condition(lambda _, x: False)]),
        ])

        root = generator.compose_nested()
        result = root.evaluate(
            SimulationPayload(
                computational_unit=1,
                collected_data=CollectedData(),
                operation_history={}))

        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].computational_unit, 4)
        self.assertEqual(result[1].computational_unit, 3)
        self.assertEqual(result[2].computational_unit, 2)
        self.assertEqual(result[3].computational_unit, 2)
