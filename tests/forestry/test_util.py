import unittest
from typing import Callable, List, Tuple

import numpy as np

DEFAULT_TIMBER_PRICE_TABLE = np.array(
                        [[  1., 160., 370.,  55.],
                        [  1., 160., 400.,  57.],
                        [  1., 160., 430.,  59.],
                        [  1., 160., 460.,  59.],
                        [  2.,  70., 300.,  17.]])

TIMBER_PRICE_TABLE_THREE_GRADES = np.array(
                        [[  1., 160., 370.,  55.],
                        [  1., 160., 400.,  57.],
                        [  1., 160., 430.,  59.],
                        [  1., 160., 460.,  59.],
                        [  2.,  70., 300.,  17.],
                        [  2.,  70., 270.,  15.],
                        [  3.,  70., 220.,  10.]
                        ])

class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: List[Tuple], fn: Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)

class TestCaseExtension(unittest.TestCase):
    def assertListsAlmostEqual(self, first: List, second: List, places: int):
        self.assertEqual(len(first), len(second))
        for i in range(len(first)):
            self.assertAlmostEqual(first[i], second[i], places=places)
