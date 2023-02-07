import unittest
from dataclasses import dataclass
from typing import Optional
from copy import copy, deepcopy
from lukefi.metsi.data.layered_model import LayeredObject


@dataclass
class ExampleType:
    i: int = 1
    f: float = 1.0
    s: str = '1'
    n: Optional = None


class LayeredModelTest(unittest.TestCase):
    def test_construction_with_overlay(self):
        level0 = ExampleType()
        level1 = LayeredObject[ExampleType](level0)
        level1.i = 10
        level2 = level1.new_layer()
        level2.s = '10'
        level3 = level2.new_layer()
        level3.n = 1000
        self.assertEqual(1, level0.i)
        self.assertEqual(10, level1.i)
        self.assertEqual(10, level2.i)
        self.assertEqual(10, level3.i)
        self.assertEqual(1.0, level0.f)
        self.assertEqual(1.0, level1.f)
        self.assertEqual(1.0, level2.f)
        self.assertEqual(1.0, level3.f)
        self.assertEqual('1', level0.s)
        self.assertEqual('1', level1.s)
        self.assertEqual('10', level2.s)
        self.assertEqual('10', level3.s)
        self.assertEqual(None, level0.n)
        self.assertEqual(None, level1.n)
        self.assertEqual(None, level2.n)
        self.assertEqual(1000, level3.n)
        self.assertRaises(AttributeError, lambda: level3.x)

    def test_fixate(self):
        level0 = ExampleType()
        level1 = LayeredObject[ExampleType](level0)
        level1.i = 10
        level2 = level1.new_layer()
        level2.s = '10'
        level3 = level2.new_layer()
        level3.n = 1000
        result = level3.fixate()
        self.assertEqual(level0.i, result.i)
        self.assertEqual(10, result.i)
        self.assertEqual(level0.f, result.f)
        self.assertEqual(1.0, result.f)
        self.assertEqual(level0.s, result.s)
        self.assertEqual('10', result.s)
        self.assertEqual(level0.n, result.n)
        self.assertEqual(1000, result.n)
