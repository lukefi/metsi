import unittest
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.forestry.harvest import thinning
from lukefi.metsi.forestry import forestry_utils as futil


class ThinningTest(unittest.TestCase):

    def test_iterative_thinning(self):
        species = [ TreeSpecies(i) for i in [1,2,3] ]
        diameters = [ 20.0 + i for i in range(0, 3) ]
        stems = [ 200.0 + i for i in range(0, 3) ]
        heights = [ 25.0 + i for i in range(0, 3) ]
        ids = ["tree-1", "tree-2", "tree-3"]
        stand = ForestStand()
        stand.reference_trees = [
            ReferenceTree(species=spe, breast_height_diameter=d, stems_per_ha=f, identifier=id)
            for spe, d, f, id in zip(species, diameters, stems, ids)
        ]
        thinning_factor = 0.97
        basal_area_upper_bound = 18.0
        thin_predicate = lambda stand: basal_area_upper_bound < futil.overall_basal_area(stand.reference_trees)
        extra_factor_solver = lambda i, n ,c: 0
        thinning.iterative_thinning(stand, thinning_factor, thin_predicate, extra_factor_solver)
        self.assertEqual(3, len(stand.reference_trees))
        self.assertEqual(171.747, round(stand.reference_trees[0].stems_per_ha, 3))
        self.assertEqual(172.606, round(stand.reference_trees[1].stems_per_ha, 3))
        self.assertEqual(173.464, round(stand.reference_trees[2].stems_per_ha, 3))
