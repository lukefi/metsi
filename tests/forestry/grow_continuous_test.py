import unittest

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.forestry.naturalprocess.grow_continuous import continuous_growth_r

@unittest.skip("Not working")
class ContinuousGrowthTest(unittest.TestCase):
    def test_pukkala_grow(self):
        fixture = ForestStand(
            identifier="1234",
            degree_days=1234.0,
            geo_location=(6555234.0, 3290233, 79.0, "EPSG:3067"),
            site_type_category=1,
            soil_peatland_category=1
        )
        fixture.reference_trees = [
            ReferenceTree(
                identifier='1234-1-tree',
                height=10.4,
                breast_height_diameter=20.3,
                breast_height_age=7,
                species=TreeSpecies.PINE,
                biological_age=23.0,
                stems_per_ha=52.3,
                tree_number=1),
            ReferenceTree(
                identifier='1234-2-tree',
                height=13.4,
                breast_height_diameter=14.3,
                breast_height_age=7,
                species=TreeSpecies.SILVER_BIRCH,
                biological_age=27.0,
                stems_per_ha=0,
                tree_number=2)
        ]

        result = continuous_growth_r(fixture, 20)
        self.assertEqual(6, len(result.reference_trees))
        result2 = continuous_growth_r(result)
        ...
