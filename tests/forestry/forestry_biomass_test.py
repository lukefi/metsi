import unittest

from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand, ReferenceTree
import pandas as pd
import forestry.biomass_repola as biomass
import os


class ForestryOperationsTest(unittest.TestCase):

    def test_stump_diameter(self):
        tree = ReferenceTree()
        tree.breast_height_diameter = 20
        self.assertAlmostEqual(biomass.stump_diameter(tree), 27)

    def test_stem_wood_biomass_vol_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        stand = ForestStand(degree_days=1150)
        volume = 0.54
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_1(tree, stand, volume)[0], 3), 0.155)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_1(tree, stand, volume)[1], 3), 0.022)

    def test_stem_wood_biomass_vol_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        stand = ForestStand(degree_days=1150)
        volume = 0.54
        volwaste = 0.003785382
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_2(tree, stand, volume, volwaste)[0], 3), 0.177)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_2(tree, stand, volume, volwaste)[1], 3), 0.176)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_2(tree, stand, volume, volwaste)[2], 3), 0.001)

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

    def test_dead_branches_biomass_2b(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.dead_branches_biomass_2b(tree), 3), 0.008)

    def test_foliage_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.foliage_biomass_1(tree), 3), 0.037)

    def test_foliage_biomass_2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.foliage_biomass_2(tree), 3), 0.035)

    def test_foliage_biomass_2b(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        tree.lowest_living_branch_height = tree.height - (0.848791838 * tree.height)
        self.assertAlmostEqual(round(biomass.foliage_biomass_2b(tree), 3), 0.034)

    def test_stump_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.stump_biomass_1(tree), 3), 0.023)

    def test_stump_biomass_1b(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.stump_biomass_1b(tree), 3), 0.023)

    def test_roots_biomass_1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.roots_biomass_1(tree), 3), 0.081)

    def test_roots_biomass_1b(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        self.assertAlmostEqual(round(biomass.roots_biomass_1b(tree), 3), 0.081)

    def test_biomass_component_models_against_OPEMOTTI_sums(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "MOTTI_biomassat.csv")
        df = pd.read_csv(input_file_path)
        stand = ForestStand()
        stand.degree_days = 1150
        for i in range(0, len(df["LPM"])):
            tree = ReferenceTree()
            tree.species = TreeSpecies(df["puulaji"][i])
            tree.breast_height_diameter = df["LPM"][i]
            tree.height = df["Pituus"][i]
            tree.lowest_living_branch_height = tree.height - (df["Latvussuhde"][i] * tree.height)
            tree.breast_height_age = df["Ika13"][i]
            tree.biological_age = df["Ika"][i]
            stand.reference_trees.append(tree)
        stem_with_bark = []
        stem_roundwood_with_bark = []
        stem_waste_with_bark = []
        living_branches = []
        dead_branches = []
        foliage = []
        stump = []
        coarse_roots = []
        for j in range(0, len(df["LPM"])):
            stem_biomass = biomass.stem_wood_biomass_vol_2(stand.reference_trees[j], stand, df["Tilavuus"][j],
                                                           df["Hukka"][j])
            stem_with_bark.append(stem_biomass[0])
            stem_roundwood_with_bark.append(stem_biomass[1])
            stem_waste_with_bark.append(stem_biomass[2])
            living_branches.append(biomass.living_branches_biomass_2(stand.reference_trees[j]))
            dead_branches.append(biomass.dead_branches_biomass_2b(stand.reference_trees[j]))
            foliage.append(biomass.foliage_biomass_2b(stand.reference_trees[j]))
            stump.append(biomass.stump_biomass_1b(stand.reference_trees[j]))
            coarse_roots.append(biomass.roots_biomass_1b(stand.reference_trees[j]))
        self.assertLess(abs(sum(stem_with_bark) - sum(df["runko kuorineen"])), 1)
        self.assertLess(abs(sum(stem_roundwood_with_bark) - sum(df["runko aines"])), 1)
        self.assertLess(abs(sum(stem_waste_with_bark) - sum(df["runko hukka"])), 0.1)
        self.assertLess(abs(sum(living_branches) - sum(df["elävät oksat"])), 0.01)
        self.assertLess(abs(sum(dead_branches) - sum(df["kuolleet oksat"])), 0.01)
        self.assertLess(abs(sum(foliage) - sum(df["lehdet"])), 1)
        self.assertLess(abs(sum(stump) - sum(df["kannot"])), 0.01)
        self.assertLess(abs(sum(coarse_roots) - sum(df["juuret_karkea"])), 0.01)

    def test_models_against_MELA(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "biomassat_MELA_3.csv")
        df = pd.read_csv(input_file_path, sep=";", header=0)
        df = df.reset_index()
        trees = []
        for i in range(0, len(df["d"])):
            tree = ReferenceTree()
            tree.species = TreeSpecies(df["ipl"][i])
            tree.breast_height_diameter = df["d"][i]
            tree.height = df["h"][i]
            tree.lowest_living_branch_height = tree.height - (df["cr"][i] * tree.height)
            tree.breast_height_age = df["t"][i]
            trees.append(tree)
        stand = ForestStand()
        stand.reference_trees = trees
        stand.degree_days = 1150
        stem_roundwood = []
        stem_bark = []
        living_branches = []
        dead_branches = []
        foliage = []
        stump = []
        coarse_roots = []
        for j in range(0, len(df["d"])):
            stem = biomass.stem_wood_biomass_vol_1(stand.reference_trees[j], stand, df["v"][j])
            stem_roundwood.append(stem[0])
            stem_bark.append(stem[1])
            living_branches.append(biomass.living_branches_biomass_2(stand.reference_trees[j]))
            dead_branches.append(biomass.dead_branches_biomass_1(stand.reference_trees[j]))
            foliage.append(biomass.foliage_biomass_2b(stand.reference_trees[j]))
            stump.append(biomass.stump_biomass_1(stand.reference_trees[j]))
            coarse_roots.append(biomass.roots_biomass_1(stand.reference_trees[j]))
        self.assertLess(abs(sum(stem_roundwood) - sum(df["runko"])), 0.001)
        self.assertLess(abs(sum(stem_bark) - sum(df["kuori"])), 0.002)
        self.assertLess(abs(sum(living_branches) - sum(df["elavat oksat"])), 0.01)
        self.assertLess(abs(sum(foliage) - sum(df["lehdet"])), 0.01)
        self.assertLess(abs(sum(dead_branches) - sum(df["kuolleet oksat"])), 0.03)
        self.assertLess(abs(sum(stump) - sum(df["kanto"])), 0.01)
        self.assertLess(abs(sum(coarse_roots) - sum(df["juuret 2 mm"])), 0.01)

    def test_tree_biomass_models3(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "MOTTI_biomassat.csv")
        df = pd.read_csv(input_file_path, index_col=0)
        trees = []
        for i in range(0, len(df["LPM"])):
            tree = ReferenceTree()
            tree.species = TreeSpecies(df["puulaji"][i])
            tree.breast_height_diameter = df["LPM"][i]
            tree.height = df["Pituus"][i]
            tree.lowest_living_branch_height = tree.height - (df["Latvussuhde"][i] * tree.height)
            tree.breast_height_age = df["Ika13"][i]
            tree.biological_age = df["Ika"][i]
            trees.append(tree)
        stand = ForestStand()
        stand.reference_trees = trees
        stand.degree_days = 1150
        biomass_totals_OPEMOTTI = []
        biomass_totals_models = []
        for i in range(0, len(df["LPM"])):
            biomass_totals_OPEMOTTI.append(
                df["runko kuorineen"][i] + df["runko aines"][i] + df["runko hukka"][i] + df["elävät oksat"][i] +
                df["kuolleet oksat"][i] + df["lehdet"][i] + df["kannot"][i] + df["juuret_karkea"][i])
            biomass_totals_models.append(
                sum(biomass.tree_biomass(stand.reference_trees[i], stand, df["Tilavuus"][i], df["Hukka"][i], 3)))
        self.assertLess(abs(sum(biomass_totals_models) - sum(biomass_totals_OPEMOTTI)), 1.32)

    def test_tree_biomass_models4(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "biomassat_MELA_3.csv")
        df = pd.read_csv(input_file_path, sep=";", header=0)
        trees = []
        for i in range(0, len(df["d"])):
            tree = ReferenceTree()
            tree.species = TreeSpecies(df["ipl"][i])
            tree.breast_height_diameter = df["d"][i]
            tree.height = df["h"][i]
            tree.lowest_living_branch_height = tree.height - (df["cr"][i] * tree.height)
            tree.breast_height_age = df["t"][i]
            trees.append(tree)
        stand = ForestStand()
        stand.reference_trees = trees
        stand.degree_days = 1150
        biomass_totals_MELA = []
        biomass_totals_models = []
        for i in range(0, len(df["d"])):
            biomass_totals_MELA.append(
                df["runko"][i] + df["kuori"][i] + df["elavat oksat"][i] + df["kuolleet oksat"][i] + df["lehdet"][i] +
                df["kanto"][i] + df["juuret 2 mm"][i])
            biomass_totals_models.append(sum(biomass.tree_biomass(stand.reference_trees[i], stand, df["v"][i], 0, 4)))
        self.assertLess(abs(sum(biomass_totals_models) - sum(biomass_totals_MELA)), 0.03)

    def test_tree_biomass_models1(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE)
        stand = ForestStand(degree_days=1150)
        volume = 0.54
        self.assertAlmostEqual(round(sum(biomass.tree_biomass(tree, stand, volume, 0, 1)), 3), 0.409)

    def test_tree_biomass_models2(self):
        tree = ReferenceTree(breast_height_diameter=29.4, breast_height_age=31, height=18.1, species=TreeSpecies.SPRUCE,
                             lowest_living_branch_height=2.715)
        stand = ForestStand(degree_days=1150)
        volume = 0.54
        self.assertAlmostEqual(round(sum(biomass.tree_biomass(tree, stand, volume, 0, 2)), 3), 0.380)

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
        self.assertEqual([
            2.901904782670537,
            0.2621029279780194,
            0.6212887091887855,
            0.1365537373913646,
            0.24537681591884583,
            0.26942696745250677,
            0.7720028796388301,
            0.0],
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
        self.assertEqual([
            2.6943581559391907,
            0.26525277171872336,
            0.8320845495264283,
            0.13170007427768654,
            0.3173139669940983,
            0.2649429105180369,
            0.7614991804052376,
            0.0],
            result)

    def test_biomasses_by_stand_model_set_3(self):
        stand = ForestStand(
            degree_days=890.0,
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

        result = biomass.biomasses_by_component_stand(stand, treevolumes, wastevolumes, 3)
        self.assertEqual([
            868.5028,
            781.65252,
            86.85028,
            0.8320845495264283,
            0.1783186075300313,
            0.3173139669940983,
            0.26430171061769187,
            0.7628057271488852],
            result)
