import copy
import unittest

import numpy as np

from lukefi.metsi.data.vectorize import ReferenceTrees, Strata, vectorize
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum


class TestVectorize(unittest.TestCase):

    before: list[ForestStand]

    @classmethod
    def setUpClass(cls) -> None:
        cls.before = [ForestStand(reference_trees=[ReferenceTree(species=TreeSpecies(1)),
                                                   ReferenceTree(species=TreeSpecies(2))]),
                      ForestStand(reference_trees=[ReferenceTree(species=TreeSpecies(3)),
                                                   ReferenceTree(species=TreeSpecies(4))],
                                  tree_strata=[TreeStratum(species=TreeSpecies(1)),
                                               TreeStratum(species=TreeSpecies(2))]),
                      ForestStand(tree_strata=[TreeStratum(species=TreeSpecies(3)),
                                               TreeStratum(species=TreeSpecies(4))])]

    def setUp(self) -> None:
        self.after = copy.deepcopy(TestVectorize.before)
        vectorize(self.after)

    def test_types(self):
        self.assertIsInstance(TestVectorize.before[0].reference_trees, list)
        self.assertIsInstance(TestVectorize.before[0].tree_strata, list)
        self.assertIsInstance(self.after[0].reference_trees_soa, ReferenceTrees)
        self.assertIsInstance(self.after[0].tree_strata_soa, Strata)
        self.assertIsNotNone(self.after[0].reference_trees_soa)
        self.assertIsNotNone(self.after[1].tree_strata_soa)
        self.assertIsInstance(self.after[0].reference_trees_soa.species, np.ndarray)
        self.assertIsInstance(self.after[1].tree_strata_soa.species, np.ndarray)

    def test_lengths(self):
        self.assertEqual(len(self.after), len(TestVectorize.before))

    def test_species(self):
        print("self.after")
        for before, after in zip(TestVectorize.before, self.after):
            for aso_tree, soa_tree_species in zip(before.reference_trees, after.reference_trees_soa.species if
                                                  after.reference_trees_soa.size > 0 else []):
                self.assertEqual(aso_tree.species, soa_tree_species)
                print("self.after")
            for aso_stratum, soa_stratum_species in zip(before.tree_strata, after.tree_strata_soa.species if
                                                        after.tree_strata_soa.size > 0 else []):
                self.assertEqual(aso_stratum.species, soa_stratum_species)
                print("self.after")
