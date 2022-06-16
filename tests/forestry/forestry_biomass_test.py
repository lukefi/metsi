import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
import pandas as pd
import forestry.biomass_repola as biomass
import os

class ForestryOperationsTest(unittest.TestCase):

    def test_stump_diameter(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 20
        self.assertAlmostEqual(biomass.stump_diameter(tree),27)

    def test_stem_wood_biomass_vol(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        stand = ForestStand()
        stand.degree_days = 1150
        volume = 0.54
        volwaste = 0.003785382
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_MOTTI(tree,stand,volume,volwaste)[0],3),0.177)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_MOTTI(tree,stand,volume,volwaste)[1],3),0.176)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_vol_MOTTI(tree,stand,volume,volwaste)[2],3),0.001)

    def test_stem_wood_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_1(tree),3),0.172)
      
    def test_stem_wood_biomass_2(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.stem_wood_biomass_2(tree),3),0.154)
     
    def test_stem_bark_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.stem_bark_biomass_1(tree),3),0.024)
     
    def test_stem_bark_biomass_2(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.stem_bark_biomass_2(tree),3),0.025)

    def test_living_branches_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.living_branches_biomass_1(tree),3),0.063)
     
    def test_living_branches_biomass_2(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.living_branches_biomass_2(tree),3),0.067)

    def test_dead_branches_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.dead_branches_biomass_1(tree),3),0.009)
     
    def test_dead_branches_biomass_2(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.dead_branches_biomass_2(tree),3),0.008)

    def test_dead_branches_biomass_MOTTI(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.dead_branches_biomass_MOTTI(tree),3),0.008)

    def test_foliage_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.foliage_biomass_1(tree),3),0.037)
     
    def test_foliage_biomass_2(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.foliage_biomass_2(tree),3),0.035)

    def test_foliage_biomass_MOTTI(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        tree.lowest_living_branch_height = tree.height-(0.848791838*tree.height)
        self.assertAlmostEqual(round(biomass.foliage_biomass_MOTTI(tree),3),0.034)

    def test_stump_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.stump_biomass_1(tree),3),0.023)
    
    def test_stump_biomass_MOTTI(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.stump_biomass_MOTTI(tree),3),0.023)
     
    def test_roots_biomass_1(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.roots_biomass_1(tree),3),0.081)
    
    def test_roots_biomass_MOTTI(self):
        tree=ReferenceTree()
        tree.breast_height_diameter = 29.4
        tree.breast_height_age = 31
        tree.height = 18.1
        tree.species = 2
        self.assertAlmostEqual(round(biomass.roots_biomass_MOTTI(tree),3),0.081)
    
    def test_biomass_component_models_against_OPEMOTTI_sums(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "MOTTI_biomassat.csv")
        df = pd.read_csv(input_file_path)
        trees = []
        for i in range(0,len(df["LPM"])):
            tree=ReferenceTree()
            tree.species = df["puulaji"][i]
            tree.breast_height_diameter = df["LPM"][i]
            tree.height = df["Pituus"][i]
            tree.lowest_living_branch_height = tree.height-(df["Latvussuhde"][i]*tree.height)
            tree.breast_height_age = df["Ika13"][i]
            tree.biological_age = df["Ika"][i]
            trees.append(tree)
        stand = ForestStand()
        stand.reference_trees = trees
        stand.degree_days = 1150
        stem_with_bark = []
        stem_roundwood_with_bark = []
        stem_waste_with_bark = []
        living_branches = []
        dead_branches = []
        foliage = []
        stump = []
        coarse_roots = []
        for j in range(0,len(df["LPM"])):
            stem_biomass = biomass.stem_wood_biomass_vol_MOTTI(stand.reference_trees[j],stand,df["Tilavuus"][j],df["Hukka"][j])
            stem_with_bark.append(stem_biomass[0])
            stem_roundwood_with_bark.append(stem_biomass[1])
            stem_waste_with_bark.append(stem_biomass[2])
            living_branches.append(biomass.living_branches_biomass_2(stand.reference_trees[j]))
            dead_branches.append(biomass.dead_branches_biomass_MOTTI(stand.reference_trees[j]))
            foliage.append(biomass.foliage_biomass_MOTTI(stand.reference_trees[j]))
            stump.append(biomass.stump_biomass_MOTTI(stand.reference_trees[j]))
            coarse_roots.append(biomass.roots_biomass_MOTTI(stand.reference_trees[j]))
        self.assertLess(abs(sum(stem_with_bark)-sum(df["runko kuorineen"])), 1)
        self.assertLess(abs(sum(stem_roundwood_with_bark)-sum(df["runko aines"])), 1)
        self.assertLess(abs(sum(stem_waste_with_bark)-sum(df["runko hukka"])), 0.1)
        self.assertLess(abs(sum(living_branches)-sum(df["elävät oksat"])), 0.01)
        self.assertLess(abs(sum(dead_branches)-sum(df["kuolleet oksat"])), 0.01)
        self.assertLess(abs(sum(foliage)-sum(df["lehdet"])), 1)
        self.assertLess(abs(sum(stump)-sum(df["kannot"])), 0.01)
        self.assertLess(abs(sum(coarse_roots)-sum(df["juuret_karkea"])), 0.01)
    
    def test_MOTTI_models_against_MELA_sums(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "biomassat_MELA_3.csv")
        df = pd.read_csv(input_file_path,sep=";",header=0)
        df = df.reset_index()
        trees = []
        for i in range(0,len(df["d"])):
            tree=ReferenceTree()
            tree.species = df["ipl"][i]
            tree.breast_height_diameter = df["d"][i]
            tree.height = df["h"][i]
            tree.lowest_living_branch_height = tree.height-(df["cr"][i]*tree.height)
            tree.breast_height_age = df["t"][i]
            trees.append(tree)
        stand = ForestStand()
        stand.reference_trees = trees
        stand.degree_days = 1150
        stem_with_bark = []
        stem_roundwood_with_bark = []
        stem_waste_with_bark = []
        living_branches = []
        dead_branches = []
        foliage = []
        stump = []
        coarse_roots = []
        for j in range(0,len(df["d"])):
            stem_biomass = biomass.stem_wood_biomass_vol_MOTTI(stand.reference_trees[j],stand,df["v"][j],df["vv"][j])
            stem_with_bark.append(stem_biomass[0])
            stem_roundwood_with_bark.append(stem_biomass[1])
            stem_waste_with_bark.append(stem_biomass[2])
            living_branches.append(biomass.living_branches_biomass_2(stand.reference_trees[j]))
            dead_branches.append(biomass.dead_branches_biomass_MOTTI(stand.reference_trees[j]))
            foliage.append(biomass.foliage_biomass_MOTTI(stand.reference_trees[j]))
            stump.append(biomass.stump_biomass_MOTTI(stand.reference_trees[j]))
            coarse_roots.append(biomass.roots_biomass_MOTTI(stand.reference_trees[j]))
        print("MOTTI:")
        print("stem, with bark:")
        print(round(sum(stem_with_bark),1))
        print("stem, roundwood with bark:")
        print(round(sum(stem_roundwood_with_bark),1))
        print("stem, waste with bark:")
        print(round(sum(stem_waste_with_bark),1))
        print("living branches")
        print(round(sum(living_branches),1))
        print("dead branches")
        print(round(sum(dead_branches),1))
        print("kanto")
        print(round(sum(stump),1))
        print("juuret 2mm")
        print(round(sum(coarse_roots),1))
        self.assertLess(abs(sum(living_branches)-sum(df["elavat oksat"])), 1)
        self.assertLess(abs(sum(foliage)-sum(df["lehdet"])), 1)
        self.assertLess(abs(sum(dead_branches)-sum(df["kuolleet oksat"])), 4)
        self.assertLess(abs(sum(stump)-sum(df["kanto"])), 1)
        self.assertLess(abs(sum(coarse_roots)-sum(df["juuret 2 mm"])), 1)

    def test_MELA_models(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "biomassat_MELA_3.csv")
        df = pd.read_csv(input_file_path,sep=";",header=0)
        df = df.reset_index()
        trees = []
        for i in range(0,len(df["d"])):
            tree=ReferenceTree()
            tree.species = df["ipl"][i]
            tree.breast_height_diameter = df["d"][i]
            tree.height = df["h"][i]
            tree.lowest_living_branch_height = tree.height-(df["cr"][i]*tree.height)
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
        for j in range(0,len(df["d"])):
            stem = biomass.stem_wood_biomass_vol_MELA_2(stand.reference_trees[j],stand,df["v"][j])
            stem_roundwood.append(stem[0])
            stem_bark.append(stem[1])
            living_branches.append(biomass.living_branches_biomass_2(stand.reference_trees[j]))
            dead_branches.append(biomass.dead_branches_biomass_1(stand.reference_trees[j]))
            foliage.append(biomass.foliage_biomass_MOTTI(stand.reference_trees[j]))
            stump.append(biomass.stump_biomass_1(stand.reference_trees[j]))
            coarse_roots.append(biomass.roots_biomass_1(stand.reference_trees[j]))
        print("MELA:")
        print("stem, roundwood:")
        print(round(sum(stem_roundwood),1))
        print("stem, bark:")
        print(round(sum(stem_bark),1))
        print("living branches")
        print(round(sum(living_branches),1))
        print("dead branches")
        print(round(sum(dead_branches),1))
        print("kanto")
        print(round(sum(stump),1))
        print("juuret 2mm")
        print(round(sum(coarse_roots),1))
        self.assertLess(abs(sum(stem_roundwood)-sum(df["runko"])), 0.001)
        self.assertLess(abs(sum(stem_bark)-sum(df["kuori"])), 0.002)
        self.assertLess(abs(sum(living_branches)-sum(df["elavat oksat"])), 0.01)
        self.assertLess(abs(sum(foliage)-sum(df["lehdet"])), 0.01)
        self.assertLess(abs(sum(dead_branches)-sum(df["kuolleet oksat"])), 0.03)
        self.assertLess(abs(sum(stump)-sum(df["kanto"])), 0.01)
        self.assertLess(abs(sum(coarse_roots)-sum(df["juuret 2 mm"])), 0.01)



    def test_tree_biomass(self):
        input_file_path = os.path.join(os.getcwd(), "tests", "resources", "MOTTI_biomassat.csv")
        df = pd.read_csv(input_file_path,index_col=0)
        trees = []
        for i in range(0,len(df["LPM"])):
            tree=ReferenceTree()
            tree.species = df["puulaji"][i]
            tree.breast_height_diameter = df["LPM"][i]
            tree.height = df["Pituus"][i]
            tree.lowest_living_branch_height = tree.height-(df["Latvussuhde"][i]*tree.height)
            tree.breast_height_age = df["Ika13"][i]
            tree.biological_age = df["Ika"][i]
            trees.append(tree)
        stand = ForestStand()
        stand.reference_trees = trees
        stand.degree_days = 1150
        biomass_totals_OPEMOTTI = []
        biomass_totals_models = []
        for i in range(0,100):
            biomass_totals_OPEMOTTI.append(df["runko kuorineen"][i]+df["runko aines"][i]+df["runko hukka"][i]+df["elävät oksat"][i]+df["kuolleet oksat"][i]+df["lehdet"][i]+df["kannot"][i]+df["juuret_karkea"][i])
            biomass_totals_models.append(sum(biomass.tree_biomass(trees[i],stand,df["Tilavuus"][i],df["Hukka"][i],3)))
        self.assertLess(abs(sum(biomass_totals_models)-sum(biomass_totals_OPEMOTTI)), 0.03)

 



