import unittest
from sim.generators import instruction_with_options


class TestGenerators(unittest.TestCase):
    def test_instruction_with_options(self):
        value = 100
        options = [10, 20, 30]
        func = lambda x, y: x + y
        prepared_functions = instruction_with_options(func, options)
        results = []
        for f in prepared_functions:
            results.append(f(value))
        self.assertEqual([110, 120, 130], results)
