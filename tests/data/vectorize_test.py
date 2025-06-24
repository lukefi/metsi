import copy
import unittest

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
        self.assertIsInstance(self.after[0].reference_trees, ReferenceTrees)
        self.assertIsInstance(self.after[0].tree_strata, Strata)

    def test_lengths(self):
        self.assertEqual(len(self.after), len(TestVectorize.before))

    def test_species(self):
        self.assertEqual(TestVectorize.before[0].reference_trees[0].species.value,
                             self.after[0].reference_trees.species[0])
        for before, after in zip(TestVectorize.before, self.after):
            for aso_tree, soa_tree_species in zip(before.reference_trees, after.reference_trees.species if
                                after.reference_trees.size > 0 else []):
                self.assertEqual(aso_tree.species, soa_tree_species)
            for aso_stratum, soa_stratum_species in zip(before.tree_strata, after.tree_strata.species if
                                after.tree_strata.size > 0 else []):
                self.assertEqual(aso_stratum.species, soa_stratum_species)
