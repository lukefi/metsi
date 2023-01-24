import unittest

from lukefi.metsi.data.enums.internal import TreeSpecies, SiteType, SoilPeatlandCategory
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.domain.natural_processes.grow_continuous import grow_continuous


class ContinuousGrowthTest(unittest.TestCase):
    def test_grow_continuous(self):
        fixture = ForestStand(
            area=23.0,
            identifier="123443",
            degree_days=1234.0,
            geo_location=(6555234.0, 3290233, 79.0, "EPSG:3067"),
            site_type_category=SiteType(1),
            soil_peatland_category=SoilPeatlandCategory(1),
            year=2023
        )
        fixture.reference_trees = [
            ReferenceTree(
                identifier='123443-tree-1',
                height=10.4,
                breast_height_diameter=20.3,
                species=TreeSpecies.PINE,
                biological_age=23.0,
                stems_per_ha=52.3,
                tree_number=1),
            ReferenceTree(
                identifier='123443-tree-2',
                height=13.4,
                breast_height_diameter=14.3,
                species=TreeSpecies.SILVER_BIRCH,
                biological_age=27.0,
                stems_per_ha=0,
                tree_number=2)
        ]

        result, _ = grow_continuous((fixture, None))
        # TODO: this test suite is WIP
