import unittest

from sim.forestry_models import grow, cut, plant


class OperationsTest(unittest.TestCase):
    def test_grow(self):
        assertions = [
            (10000, 11085.73620475813),
            (None, None)
        ]
        for i in assertions:
            result = grow(i[0])
            self.assertEqual(i[1], result)

    def test_cut(self):
        assertions = [
            ((400, 25), 300),
            ((400, 50), 200),
            ((None, 100), None)
        ]
        for i in assertions:
            result = cut(i[0][0], i[0][1])
            self.assertEqual(i[1], result)

        self.assertRaises(Exception, lambda: cut(100, 20))

    def test_plant(self):
        assertions = [
            ((10000, 1000), 10010),
            ((20000, 5000), 20050),
            ((None, 5000), None),
        ]
        for i in assertions:
            result = plant(i[0][0], i[0][1])
            self.assertEqual(i[1], result)
