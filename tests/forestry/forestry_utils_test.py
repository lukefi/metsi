import unittest
from parameterized import parameterized
from lukefi.metsi.forestry import forestry_utils as futil
from lukefi.metsi.data.model import ReferenceTree, TreeStratum
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
            result = lukefi.metsi.forestry.forestry_utils.override_from_diameter(
                initial_stratum, current_stratum, reference_tree)
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
