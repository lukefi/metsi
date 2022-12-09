import unittest

from forestry.grow_acta import grow_acta
from forestry.grow_motti import grow_motti
from tests.test_utils import prepare_growth_test_stand

try:
    import fhk
    from forestry.grow_fhk import grow_fhk
except ImportError:
    fhk = None


class GrowthOperationsTest(unittest.TestCase):

    def assert_domain_sensibility(self, stand):
        """
        Simple sanity check that growth doesn't happen to wrong direction. Exact values for domain functions should be
        tested separately in library implementations.
        stems must never increase
        height must never decrease
        diameter must never decrease
        """
        fixture = prepare_growth_test_stand()
        for res, ref in zip(stand.reference_trees, fixture.reference_trees):
            self.assertTrue(res.stems_per_ha <= ref.stems_per_ha)
            self.assertTrue(res.breast_height_diameter >= ref.breast_height_diameter)
            self.assertTrue(res.height >= ref.height)

    @unittest.skipIf(fhk is None, "fhk not installed")
    def test_grow_fhk(self):
        stand = prepare_growth_test_stand()
        grow_fhk(
            (stand, None),
            graph="tests/resources/graph.g.lua",
            luapath="tests/resources/?.lua"
        )
        self.assert_domain_sensibility(stand)
        self.assertTrue(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[0].biological_age, 60)
        self.assertEqual(stand.reference_trees[1].biological_age, 42)
        self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 0)
        self.assertEqual(stand.year, 2030)

        # grow again to trigger tree 3 to grow from sapling to mature
        grow_fhk(
            (stand, None),
            graph="tests/resources/graph.g.lua",
            luapath="tests/resources/?.lua"
        )

        self.assertFalse(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[2].biological_age, 11)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 11)

    def test_grow_motti(self):
        stand = prepare_growth_test_stand()
        grow_motti((stand, None))
        self.assert_domain_sensibility(stand)
        self.assertFalse(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[0].biological_age, 60)
        self.assertEqual(stand.reference_trees[1].biological_age, 42)
        self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 6)
        self.assertEqual(stand.year, 2030)

    def test_grow_acta(self):
        stand = prepare_growth_test_stand()
        grow_acta((stand, None))
        self.assert_domain_sensibility(stand)
        self.assertTrue(stand.reference_trees[2].sapling)
        # grow_acta doesn't increase ages at this moment. needs FFL change
        # self.assertEqual(stand.reference_trees[0].biological_age, 60)
        # self.assertEqual(stand.reference_trees[1].biological_age, 42)
        # self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        # self.assertEqual(stand.reference_trees[2].breast_height_age, 0)
        self.assertEqual(stand.year, 2030)
