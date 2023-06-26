import unittest
from parameterized import parameterized
from lukefi.metsi.forestry import forestry_utils as futil
from lukefi.metsi.data.model import ReferenceTree, ForestStand, TreeStratum
from lukefi.metsi.data.enums.internal import TreeSpecies, Storey
import lukefi.metsi.forestry.forestry_utils

def strata_fixture() -> list[TreeStratum]:
    values = [
        {'species': TreeSpecies.SPRUCE, 'storey': Storey.DOMINANT, 'mean_diameter': 10.0},
        {'species': TreeSpecies.SPRUCE, 'storey': Storey.UNDER, 'mean_diameter': 5.0},
        {'species': TreeSpecies.PINE, 'storey': Storey.DOMINANT, 'mean_diameter': 18.0},
        {'species': TreeSpecies.DOWNY_BIRCH, 'storey': Storey.UNDER, 'mean_diameter': 5.0},
        {'species': TreeSpecies.SPRUCE, 'storey': Storey.DOMINANT, 'mean_diameter': 5.0},
        {'species': TreeSpecies.COMMON_ALDER, 'storey': Storey.UNDER, 'mean_diameter': 6.2},
        {'species': TreeSpecies.COMMON_ASH, 'storey': Storey.UNDER, 'mean_diameter': 6.5},
    ]
    return [TreeStratum(**v) for v in values]

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

    def test_generate_diameter_threshold(self):
        assertions = [
            ((10.0, 20.0), 13.33333),
            ((5.0, 10.0), 6.66667),
            ((0.0, 10.0), 0.0),
            ((5.0, 0.0), 0.0)
        ]

        for i in assertions:
            result = round(lukefi.metsi.forestry.forestry_utils.generate_diameter_threshold(i[0][0], i[0][1]), 5)
            self.assertEqual(result, i[1])

    def test_override_from_diameter(self):
        initial_stratum = TreeStratum()
        initial_stratum.mean_diameter = 10.0
        current_stratum = TreeStratum()
        current_stratum.mean_diameter = 20.0
        assertions = [
            (13.0, current_stratum),
            (15.0, initial_stratum),
        ]
        for i in assertions:
            reference_tree = ReferenceTree()
            reference_tree.breast_height_diameter = i[0]
            result = lukefi.metsi.forestry.forestry_utils.override_from_diameter(initial_stratum, current_stratum, reference_tree)
            self.assertEqual(i[1], result)

    def test_find_matching_stratum_by_diameter(self):
        reference_tree = ReferenceTree()
        reference_tree.species = TreeSpecies.SPRUCE
        reference_tree.breast_height_diameter = 13.0

        strata = [stratum for stratum in strata_fixture() if stratum.species == TreeSpecies.SPRUCE]
        result = lukefi.metsi.forestry.forestry_utils.find_matching_stratum_by_diameter(reference_tree, strata)
        self.assertEqual(strata[0], result)

    def test_find_strata_for_black_spruce(self):
        strata = strata_fixture()
        result = lukefi.metsi.forestry.forestry_utils.find_strata_by_similar_species(TreeSpecies.BLACK_SPRUCE, strata)
        self.assertEqual(4, len(result))
        for stratum in result:
            self.assertTrue(stratum.species.is_coniferous())

    def test_find_strata_for_silver_birch(self):
        strata = strata_fixture()
        result = lukefi.metsi.forestry.forestry_utils.find_strata_by_similar_species(TreeSpecies.SILVER_BIRCH, strata)
        self.assertEqual(1, len(result))
        self.assertEqual(TreeSpecies.DOWNY_BIRCH, result[0].species)

    def test_find_strata_for_bay_willow(self):
        strata = strata_fixture()
        result = lukefi.metsi.forestry.forestry_utils.find_strata_by_similar_species(TreeSpecies.BAY_WILLOW, strata)
        self.assertEqual(3, len(result))
        for stratum in result:
            self.assertTrue(stratum.species.is_deciduous())

    @parameterized.expand([
        [6, 4],
        [7, 0],
        [13, 0],
        [17, 0]
    ])
    def test_find_matching_storey_stratum_for_spruce(self, diameter, expected_stratum_index):
        reference_tree = ReferenceTree()
        reference_tree.storey = Storey.DOMINANT
        reference_tree.species = TreeSpecies.SPRUCE
        reference_tree.breast_height_diameter = diameter

        strata = strata_fixture()
        result = lukefi.metsi.forestry.forestry_utils.find_matching_storey_stratum_for_tree(reference_tree, strata)
        self.assertEqual(strata[expected_stratum_index], result)

    @parameterized.expand([
        [7.2, None],  # 7.2 is below threshold for 18 cm mean_diameter
        [7.3, 2],
        [10, 2],
        [15, 2],
        [44.9, 2],
        [45, None]  # 45 is beyond threshold for 18 cm mean_diameter
    ])
    def test_find_matching_storey_stratum_for_pine(self, diameter, expected_stratum_index):
        reference_tree = ReferenceTree()
        reference_tree.storey = Storey.DOMINANT
        reference_tree.species = TreeSpecies.PINE
        reference_tree.breast_height_diameter = diameter

        strata = strata_fixture()
        result = lukefi.metsi.forestry.forestry_utils.find_matching_storey_stratum_for_tree(reference_tree, strata)
        if expected_stratum_index is not None:
            self.assertEqual(strata[expected_stratum_index], result)
        else:
            self.assertEqual(None, result)
