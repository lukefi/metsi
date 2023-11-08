from types import SimpleNamespace
import unittest
from parameterized import parameterized
from lukefi.metsi.data.model import ReferenceTree, ForestStand, TreeStratum
from lukefi.metsi.data.conversion.internal2mela import land_use_mapper, soil_peatland_mapper, species_mapper, \
    owner_mapper, mela_stand
from lukefi.metsi.data.enums.internal import LandUseCategory, OwnerCategory, SiteType, SoilPeatlandCategory, TreeSpecies
from lukefi.metsi.data.enums.mela import MelaLandUseCategory, MelaOwnerCategory, MelaSoilAndPeatlandCategory, MelaTreeSpecies


class Internal2MelaTest(unittest.TestCase):
    def test_species_good(self):
        fixture = ReferenceTree()
        fixture.species = TreeSpecies.THUJA
        result = species_mapper(fixture)
        self.assertEqual(MelaTreeSpecies.OTHER_CONIFEROUS, result.species)

    def test_species_unknown(self):
        fixture = ReferenceTree()
        fixture.species = None
        result = species_mapper(fixture)
        self.assertEqual(MelaTreeSpecies.OTHER_DECIDUOUS, result.species)

    def test_stand_species_conversion(self):
        fixture = ForestStand(geo_location=(6654200, 102598, 0.0, "EPSG:3067"), area_weight=100.0, auxiliary_stand=True)
        tree = ReferenceTree(species=TreeSpecies.SPRUCE, stand=fixture)
        stratum = TreeStratum(species=TreeSpecies.PINE, stand=fixture)
        fixture.reference_trees.append(tree)
        fixture.tree_strata.append(stratum)
        result = mela_stand(fixture)
        self.assertEqual(MelaTreeSpecies.NORWAY_SPRUCE, result.reference_trees[0].species)
        self.assertEqual(MelaTreeSpecies.SCOTS_PINE, result.tree_strata[0].species)
        self.assertEqual((6654.2, 102.598, 0.0, "EPSG:3067"), result.geo_location)
        self.assertEqual(100.0, result.area_weight)

    @parameterized.expand([
        (OwnerCategory.METSAHALLITUS, MelaOwnerCategory.STATE),
        (OwnerCategory.UNKNOWN, MelaOwnerCategory.PRIVATE)
    ])
    def test_owner_category(self, before, after):
        fixture = SimpleNamespace(owner_category=before)
        result = owner_mapper(fixture)
        self.assertEqual(result.owner_category, after)

    @parameterized.expand([
        (LandUseCategory.FOREST, MelaLandUseCategory.FOREST_LAND),
        (LandUseCategory.ROAD, MelaLandUseCategory.ROADS_OR_ELECTRIC_LINES),
        (LandUseCategory.REAL_ESTATE, MelaLandUseCategory.BUILT_UP_LAND),
        (LandUseCategory.OTHER_LAND, MelaLandUseCategory.ROADS_OR_ELECTRIC_LINES),
        (LandUseCategory.WATER_BODY, MelaLandUseCategory.LAKES_AND_RIVERS),
    ])
    def test_land_use_category(self, lu_category, expected):
        fixture = SimpleNamespace(land_use_category=lu_category)
        result = land_use_mapper(fixture)
        self.assertEqual(result.land_use_category, expected)


    @parameterized.expand([
        (SoilPeatlandCategory.TREELESS_MIRE, SiteType.BARREN_SITE, MelaSoilAndPeatlandCategory.PEATLAND_BARREN_TREELESS_MIRE), 
        (SoilPeatlandCategory.TREELESS_MIRE, SiteType.VERY_RICH_SITE, MelaSoilAndPeatlandCategory.PEATLAND_RICH_TREELESS_MIRE),
        (SoilPeatlandCategory.TREELESS_MIRE, SiteType.DAMP_SITE, MelaSoilAndPeatlandCategory.PEATLAND_RICH_TREELESS_MIRE),
        (SoilPeatlandCategory.TREELESS_MIRE, SiteType.SUB_DRY_SITE, MelaSoilAndPeatlandCategory.PEATLAND_BARREN_TREELESS_MIRE),
        (SoilPeatlandCategory.TREELESS_MIRE, None, None),
        (SoilPeatlandCategory.MINERAL_SOIL, SiteType.TUNTURIKOIVIKKO, MelaSoilAndPeatlandCategory.MINERAL_SOIL),

    ])
    def test_soil_peatland_category(self, sp_code, st_code, expected):
        fixture = SimpleNamespace(
            soil_peatland_category=sp_code,
            site_type_category=st_code
            )
        result = soil_peatland_mapper(fixture)
        self.assertEqual(result.soil_peatland_category, expected)
