import unittest
import numpy as np

from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.vectorize import vectorize
from lukefi.metsi.domain.natural_processes.grow_acta import grow_acta, grow_acta_vectorized
from lukefi.metsi.sim.core_types import CollectedData
from tests.test_utils import prepare_growth_test_stand


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
    
    def assert_domain_sensibility_vectorized(self, stand: ForestStand):
        fixture = vectorize([prepare_growth_test_stand()])[0]
        self.assertTrue(np.all(np.less_equal(stand.reference_trees_soa.stems_per_ha , fixture.reference_trees_soa.stems_per_ha)))
        self.assertTrue(np.all(np.greater_equal(stand.reference_trees_soa.breast_height_diameter , fixture.reference_trees_soa.breast_height_diameter)))
        self.assertTrue(np.all(np.greater_equal(stand.reference_trees_soa.height , fixture.reference_trees_soa.height)))

    def assert_domain_sensibility_vectorized(self, stand: ForestStand):
        fixture = vectorize([prepare_growth_test_stand()])[0]
        self.assertTrue(
            np.all(stand.reference_trees_soa.stems_per_ha <= fixture.reference_trees_soa.stems_per_ha))
        self.assertTrue(np.all(stand.reference_trees_soa.breast_height_diameter >=
                               fixture.reference_trees_soa.breast_height_diameter))
        self.assertTrue(np.all(stand.reference_trees_soa.height >= fixture.reference_trees_soa.height))

    def test_grow_acta(self):
        stand = prepare_growth_test_stand()
        grow_acta((stand, None))
        self.assert_domain_sensibility(stand)
        self.assertFalse(stand.reference_trees[2].sapling)
        self.assertEqual(stand.reference_trees[0].biological_age, 60)
        self.assertEqual(stand.reference_trees[1].biological_age, 42)
        self.assertEqual(stand.reference_trees[2].biological_age, 6)
        self.assertEqual(stand.reference_trees[0].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[1].breast_height_age, 15)
        self.assertEqual(stand.reference_trees[2].breast_height_age, 6)
        self.assertEqual(stand.year, 2030)

    def test_grow_acta_vectorized(self):
        stand = prepare_growth_test_stand()
        stand = vectorize([stand])[0]
        grow_acta_vectorized((stand, CollectedData()))
        self.assert_domain_sensibility_vectorized(stand)
        self.assertFalse(stand.reference_trees_soa.sapling[2])
        self.assertEqual(stand.reference_trees_soa.biological_age[0], 60)
        self.assertEqual(stand.reference_trees_soa.biological_age[1], 42)
        self.assertEqual(stand.reference_trees_soa.biological_age[2], 6)
        self.assertEqual(stand.reference_trees_soa.breast_height_age[0], 15)
        self.assertEqual(stand.reference_trees_soa.breast_height_age[1], 15)
        self.assertEqual(stand.reference_trees_soa.breast_height_age[2], 6)
        self.assertEqual(stand.year, 2030)