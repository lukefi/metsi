import unittest

import numpy as np
from lukefi.metsi.data.model import ReferenceTree
from lukefi.metsi.data.vector_model import ReferenceTrees
from lukefi.metsi.forestry.naturalprocess import grow_acta


class GrowActaTest(unittest.TestCase):
    def test_yearly_diameter_growth_by_species(self):
        breast_height_diameter = 10.0
        height = 12.0
        biological_age_aggregate = 35.0
        d13_aggregate = 34.0
        height_aggregate = 33.0
        dominant_height = 15.0
        basal_area_total = 32.0
        assertations_by_species = [
            (1, 1.4766),
            (2, 2.9096)
        ]
        for i in assertations_by_species:
            result = grow_acta.yearly_diameter_growth_by_species(
                i[0],
                breast_height_diameter,
                height,
                biological_age_aggregate,
                d13_aggregate,
                height_aggregate,
                dominant_height,
                basal_area_total)
            self.assertEqual(i[1], np.round(result, 4))

    def test_yearly_height_growth_by_species(self):
        breast_height_diameter = 10.0
        height = 12.0
        biological_age_aggregate = 35.0
        d13_aggregate = 34.0
        height_aggregate = 33.0
        basal_area_total = 32.0
        assertations_by_species = [
            (1, 3.9595),
            (2, 1.5397)
        ]
        for i in assertations_by_species:
            result = grow_acta.yearly_height_growth_by_species(
                i[0],
                breast_height_diameter,
                height,
                biological_age_aggregate,
                d13_aggregate,
                height_aggregate,
                basal_area_total)
            self.assertEqual(i[1], np.round(result, 4))

    def test_grow_diameter_and_height(self):
        diameters = np.array([20.0 + i for i in range(1,6)])
        heights = np.array([22.0 + i for i in range(1,6)])
        stems = np.array([200.0 + i*50 for i in range(1,6)])
        species = np.array([1,2,1,1,2])
        ages = np.array([50.0 + i for i in range(1,6)])
        reference_trees = ReferenceTrees()
        reference_trees.breast_height_diameter = diameters
        reference_trees.height = heights
        reference_trees.stems_per_ha = stems
        reference_trees.species = species
        reference_trees.biological_age = ages
        reference_trees.size = 5
        resd, resh = grow_acta.grow_diameter_and_height(reference_trees)
        self.assertAlmostEqual(21.5682, resd[0], places=4)
        self.assertAlmostEqual(24.1751, resh[0], places=4)
        self.assertAlmostEqual(22.8763, resd[1], places=4)
        self.assertAlmostEqual(24.3788, resh[1], places=4)
        self.assertAlmostEqual(23.6416, resd[2], places=4)
        self.assertAlmostEqual(26.1624, resh[2], places=4)

    def test_grow_sapling(self):
        diameters = np.array([1.0, 1.1, 1.2])
        heights = np.array([0.5, 0.9, 1.2])
        sapling_trees = ReferenceTrees()
        sapling_trees.breast_height_diameter = diameters
        sapling_trees.height = heights
        sapling_trees.size = 2
        resd, resh = grow_acta.grow_diameter_and_height(sapling_trees, step=1)
        self.assertEqual(1.0, resd[0])
        self.assertEqual(1.1, resd[1])
        self.assertEqual(1.2, resd[2])
        self.assertEqual(0.8, resh[0])
        self.assertEqual(1.2, resh[1])
        self.assertEqual(1.5, resh[2])
