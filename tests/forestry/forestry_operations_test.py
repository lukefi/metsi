import unittest
from forestdatamodel import ForestStand, ReferenceTree
from forestry.grow_acta import grow_acta, yearly_diameter_growth_by_species, yearly_height_growth_by_species


class ForestryOperationsTest(unittest.TestCase):
    def test_grow(self):
        species = [1, 1, 2, 3, 3]
        reference_trees = []
        for i in range(0, 5):
            reference_trees.append(ReferenceTree(
                species=species[i],
                breast_height_diameter=10.0+i,
                stems_per_ha=50.0+i,
                height=28.0+i,
                biological_age=20.0+i,
                sapling=False
            ))
        reference_trees.append(ReferenceTree(
            breast_height_diameter=0.0,
            height=1.2,
            sapling=True
        ))
        stand = ForestStand()
        stand.reference_trees = reference_trees
        result_stand, _ = grow_acta((stand, None))
        self.assertEqual(6, len(result_stand.reference_trees))
        self.assertEqual(13.1827, round(result_stand.reference_trees[0].breast_height_diameter, 4))
        self.assertEqual(29.8520, round(result_stand.reference_trees[0].height, 4))
        self.assertEqual(14.4723, round(result_stand.reference_trees[1].breast_height_diameter, 4))
        self.assertEqual(30.8415, round(result_stand.reference_trees[1].height, 4))
        self.assertEqual(1.5, result_stand.reference_trees[5].height)
        self.assertEqual(1.0, result_stand.reference_trees[5].breast_height_diameter)
        self.assertEqual(False, result_stand.reference_trees[5].sapling)

    def test_yearly_diameter_growth_by_species(self):
        tree = ReferenceTree()
        tree.breast_height_diameter = 10.0
        tree.height = 12.0
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
            tree.species = i[0]
            result = yearly_diameter_growth_by_species(
                tree,
                biological_age_aggregate,
                d13_aggregate,
                height_aggregate,
                dominant_height,
                basal_area_total)
            self.assertEqual(i[1], round(result, 4))

    def test_yearly_height_growth_by_species(self):
        tree = ReferenceTree()
        tree.breast_height_diameter = 10.0
        tree.height = 12.0
        biological_age_aggregate = 35.0
        d13_aggregate = 34.0
        height_aggregate = 33.0
        dominant_height = 15.0
        basal_area_total = 32.0
        assertations_by_species = [
            (1, 3.9595),
            (2, 1.5397)
        ]
        for i in assertations_by_species:
            tree.species = i[0]
            result = yearly_height_growth_by_species(
                tree,
                biological_age_aggregate,
                d13_aggregate,
                height_aggregate,
                dominant_height,
                basal_area_total)
            self.assertEqual(i[1], round(result, 4))
