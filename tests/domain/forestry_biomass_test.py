import unittest

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
import lukefi.metsi.domain.data_collection.biomass_repola as biomass

import lukefi.metsi.domain.collected_types


class ForestryOperationsTest(unittest.TestCase):

    def test_stump_diameter(self):
        tree = ReferenceTree()
        tree.breast_height_diameter = 20
        self.assertAlmostEqual(biomass.stump_diameter(tree), 27)

    def test_stem_wood_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_1(tree), 3), 0.172)

    def test_stem_wood_biomass_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.85 * tree.height)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_2(tree), 3), 0.141)

    def test_stem_bark_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.stem_bark_biomass_1(tree), 3), 0.024)

    def test_stem_bark_biomass_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.stem_bark_biomass_2(tree), 3), 0.025)

    def test_living_branches_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.living_branches_biomass_1(tree), 3), 0.063)

    def test_living_branches_biomass_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.living_branches_biomass_2(tree), 3), 0.067)

    def test_dead_branches_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.dead_branches_biomass_1(tree), 3), 0.009)

    def test_dead_branches_biomass_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.dead_branches_biomass_2(tree), 3), 0.008)

    def test_foliage_biomass_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.foliage_biomass_2(tree), 3), 0.035)

    def test_stump_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.stump_biomass_1(tree), 3), 0.023)

    def test_roots_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.roots_biomass_1(tree), 3), 0.081)

    def test_tree_biomass_models1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        volume = 0.54
        self.assertAlmostEqual(round(biomass.tree_biomass(tree, None, volume, 0, 1).total(), 3), 0.409)

    def test_tree_biomass_models2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE,
                             lowest_living_branch_height=2.715)
        volume = 0.54
        self.assertAlmostEqual(round(biomass.tree_biomass(tree, None, volume, 0, 2).total(), 3), 0.380)

    def test_biomasses_by_stand_model_set_1(self):
        stand = ForestStand(
            reference_trees=[
                ReferenceTree(
                    height=15.0,
                    species=TreeSpecies.PINE,
                    breast_height_diameter=20.0,
                    breast_height_age=10,
                    stems_per_ha=34.0
                ),
                ReferenceTree(
                    height=1.0,
                    species=TreeSpecies.PINE,
                    breast_height_diameter=2.0,
                    stems_per_ha=153.0
                )
            ]
        )

        # TODO: sanity of these values is unknown to yours truly, help needed
        treevolumes = [100.0, 10.0]
        wastevolumes = [10.0, 1.0]

        result = biomass.biomasses_by_component_stand(stand, treevolumes, wastevolumes, 1)
        self.assertEqual(lukefi.metsi.domain.collected_types.BiomassData(
            stem_wood=2.901904782670537,
            stem_bark=0.2621029279780194,
            stem_waste=0.0,
            living_branches=0.6212887091887855,
            dead_branches=0.1365537373913646,
            foliage=0.24537681591884583,
            stumps=0.26942696745250677,
            roots=0.7720028796388301),
            result)

    def test_biomasses_by_stand_model_set_2(self):
        stand = ForestStand(
            reference_trees=[
                ReferenceTree(
                    height=15.0,
                    species=TreeSpecies.PINE,
                    breast_height_diameter=20.0,
                    breast_height_age=10,
                    stems_per_ha=34.0,
                    lowest_living_branch_height=4.0
                )
            ]
        )

        # TODO: sanity of these values is unknown to yours truly, help needed
        treevolumes = [100.0, 10.0]
        wastevolumes = [10.0, 1.0]

        result = biomass.biomasses_by_component_stand(stand, treevolumes, wastevolumes, 2)
        self.assertEqual(lukefi.metsi.domain.collected_types.BiomassData(
            stem_wood=2.6943581559391907,
            stem_bark=0.26525277171872336,
            stem_waste=0.0,
            living_branches=0.8320845495264283,
            dead_branches=0.13170007427768654,
            foliage=0.3173139669940983,
            stumps=0.2649429105180369,
            roots=0.7614991804052376),
            result)

    def test_calculate_biomass_no_trees(self):
        result = biomass.biomasses_by_component_stand(ForestStand(), None, None, None)
        self.assertEqual(biomass.BiomassData(), result)
