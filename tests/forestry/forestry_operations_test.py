import unittest

from forestry.ForestDataModels import ForestStand
from forestry.operations import grow


class ForestryOperationsTest(unittest.TestCase):
    def test_grow(self):
        fixture = ForestStand()
        fixture.identifier = "123"
        result = grow(fixture)
        self.assertEqual(fixture.identifier, result.identifier)
