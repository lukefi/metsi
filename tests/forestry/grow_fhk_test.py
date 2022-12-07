from forestdatamodel.enums.internal import TreeSpecies
from forestdatamodel.model import ForestStand, ReferenceTree
import unittest
try:
    import fhk
    from forestry.grow_fhk import grow_fhk
except ImportError:
    fhk = None

@unittest.skipIf(fhk is None, "fhk not installed")
class GrowFhkTest(unittest.TestCase):

    def test_grow_fhk(self):
        stand = ForestStand(
            degree_days=1000,
            reference_trees=[
                ReferenceTree(species=TreeSpecies.PINE, stems_per_ha=123, breast_height_diameter=30, height=20),
                ReferenceTree(species=TreeSpecies.SPRUCE, stems_per_ha=123, breast_height_diameter=25, height=17)
            ]
        )
        grow_fhk(
            (stand, None),
            graph = "tests/resources/graph.g.lua",
            luapath = "tests/resources/?.lua"
        )
        self.assertEqual(stand.reference_trees[0].stems_per_ha, 100)
        self.assertEqual(stand.reference_trees[1].stems_per_ha, 100)
        self.assertEqual(stand.reference_trees[0].breast_height_diameter, 31)
        self.assertEqual(stand.reference_trees[1].breast_height_diameter, 27)
        self.assertEqual(stand.reference_trees[0].height, 20.5)
        self.assertEqual(stand.reference_trees[1].height, 18)
