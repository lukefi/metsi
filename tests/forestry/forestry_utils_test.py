import unittest
from lukefi.metsi.forestry import forestry_utils as futil
from lukefi.metsi.data.model import ReferenceTree, ForestStand
from lukefi.metsi.data.enums.internal import TreeSpecies


class ForestryUtilsTest(unittest.TestCase):

    def test_calculate_dominant_height(self):
        stems = [
            [82, 30],
            [13, 51]
        ]
        diameters = [
            [18.1, 5.7],
            [50.1, 35.9]
        ]
        assertions = [
            # over 100 stems
            ([diameters[0], stems[0]], 15.868),
            # under 100 stems
            ([diameters[1], stems[1]], 38.784375),
        ]
        for i in assertions:
            stand = ForestStand()
            fixtures = [ReferenceTree(breast_height_diameter=d, stems_per_ha=f) for d, f in zip(i[0][0], i[0][1])]
            stand.reference_trees = fixtures
            result = futil.solve_dominant_height_c_largest(stand, c=100)
            self.assertEqual(i[1], result)

    def test_overall_stems_per_ha(self):
        stand = ForestStand()
        stems = [99.0, 100.0, 101.0]
        stand.reference_trees = [
            ReferenceTree(stems_per_ha=f)
            for f in stems
            ]
        result = futil.overall_stems_per_ha(stand.reference_trees)
        self.assertEqual(300.0, result)

    def test_overall_basal_area(self):
        stand = ForestStand()
        diameters = [10.0, 11.0, 12.0]
        stems = [99, 100, 101]
        stand.reference_trees = [
            ReferenceTree(breast_height_diameter=d, stems_per_ha=f)
            for d, f in zip(diameters, stems)
            ]
        result = futil.overall_basal_area(stand.reference_trees)
        self.assertEqual(2.8702, round(result, 4))

    def test_solve_dominant_species(self):
        stand = ForestStand()
        diameters = [10.0, 11.0, 12.0]
        stems = [99, 100, 101]
        species = [1, 2, 2]
        stand.reference_trees = [
            ReferenceTree(breast_height_diameter=d, stems_per_ha=f, species=s)
            for d, f, s in zip(diameters, stems, species)
            ]
        self.assertEqual(TreeSpecies.SPRUCE, futil.solve_dominant_species(stand.reference_trees))
        self.assertEqual(None, futil.solve_dominant_species([]))

    def test_calculate_basal_area(self):
        tree = ReferenceTree()
        assertions = [
            [(10.0, 50.0), 0.3927],
            [(0.0, 50.0), 0.0],
            [(10.0, 0.0), 0.0],
            [(0.0, 0.0), 0.0]
        ]
        for i in assertions:
            tree.breast_height_diameter = i[0][0]
            tree.stems_per_ha = i[0][1]
            result = futil.calculate_basal_area(tree)
            self.assertEqual(i[1], round(result, 4))

    def test_solve_dominant_height(self):
        reference_trees = []
        for i in range(1, 6):
            reference_tree = ReferenceTree()
            reference_tree.height = 28.0 + i
            reference_trees.append(reference_tree)
        # heights are [29.0, 30.0, 31.0, 32.0, 33.0]
        result = futil.solve_dominant_height(reference_trees)
        self.assertEqual(31.0, result)

    def test_calcualte_attribute_sum(self):
        f = lambda x: x.stems_per_ha
        reference_trees = []
        for i in range(1, 6):
            reference_tree = ReferenceTree()
            reference_tree.stems_per_ha = 2.0 * i
            reference_trees.append(reference_tree)
        # stems_per_ha are [2, 4, 6, 8, 10]
        result = futil.calculate_attribute_sum(reference_trees, f)
        self.assertEqual(30, result)

    def test_calculate_basal_area_weighted_attribute_sum(self):
        """ Tests the generic function calculate_attribute_aggregate by counting the basal area weighted sum for breast height diameter for pine (species==1) """
        f = lambda x: x.breast_height_diameter * futil.calculate_basal_area(x)
        reference_trees = []
        for i in range(1, 6):
            reference_tree = ReferenceTree()
            reference_tree.species = 1
            reference_tree.breast_height_diameter = 10.0 + i
            reference_tree.stems_per_ha = 50.0 + i
            reference_trees.append(reference_tree)
        result = futil.calculate_basal_area_weighted_attribute_sum(reference_trees, f)
        self.assertEqual(13.3402, round(result, 4))

    def test_compaunded_growth_factor(self):
        assertions = [
            ((1.0, 5), 1.051),
            ((1.0, 1), 1.01),
            ((0.0, 1), 1.0),
            ((123.0, 10), 3041.226)
        ]
        for i in assertions:
            result = futil.compounded_growth_factor(i[0][0], i[0][1])
            self.assertEqual(i[1], round(result, 3))

    def test_mean_age_stand(self):
        stand = ForestStand()
        self.assertEqual(0,futil.mean_age_stand(stand))
        stand.reference_trees = []
        for i in range(1, 30):
            reference_tree = ReferenceTree()
            reference_tree.species = 1
            reference_tree.biological_age = 60 - i
            reference_tree.breast_height_diameter = 10.0 + i
            reference_tree.stems_per_ha = 50.0 + i
            stand.reference_trees.append(reference_tree)
        self.assertEqual(43.92307692307692,futil.mean_age_stand(stand))
 
