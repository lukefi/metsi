import unittest
from forestdatamodel import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from tests.test_utils import ConverterTestSuite
from forestry.thinning_limits import site_type_to_key, soil_peatland_category_to_key, species_to_key, solve_hdom_key, get_thinning_bounds
from forestry.thinning_limits import THINNING_LIMITS, SiteTypeKey, SoilPeatlandKey, SpeciesKey


class ThinningsTest(ConverterTestSuite):

    def test_site_type_to_key(self):
        assertions = [
            ([1], SiteTypeKey.OMT),
            ([2], SiteTypeKey.OMT),
            ([3], SiteTypeKey.MT),
            ([4], SiteTypeKey.VT),
            ([5], SiteTypeKey.CT),
            ([6], SiteTypeKey.CT),
            ([7], SiteTypeKey.CT),
            ([8], SiteTypeKey.CT)
        ]
        self.run_with_test_assertions(assertions, site_type_to_key)
        self.assertRaises(TypeError, site_type_to_key, 'kissa123')
        self.assertRaises(TypeError, site_type_to_key, None)

    def test_soil_peatland_cateogry_to_key(self):
        assertions = [
            ([1], SoilPeatlandKey.MINERAL_SOIL),
            ([2], SoilPeatlandKey.PEATLAND),
            ([3], SoilPeatlandKey.PEATLAND),
            ([4], SoilPeatlandKey.PEATLAND),
            ([5], SoilPeatlandKey.PEATLAND)
        ]
        self.run_with_test_assertions(assertions, soil_peatland_category_to_key)
        self.assertRaises(TypeError, site_type_to_key, 'kissa123')
        self.assertRaises(TypeError, site_type_to_key, None)

    def test_species_to_key(self):
        assertions = [
            ([TreeSpecies.PINE], SpeciesKey.PINE),
            ([TreeSpecies.SPRUCE], SpeciesKey.SPRUCE),
            ([TreeSpecies.SILVER_BIRCH], SpeciesKey.SILVER_BIRCH),
            ([TreeSpecies.DOWNY_BIRCH], SpeciesKey.DOWNY_BIRCH),
            ([TreeSpecies.OTHER_DECIDUOUS], SpeciesKey.SILVER_BIRCH),
            ([TreeSpecies.BLACK_SPRUCE], SpeciesKey.SILVER_BIRCH),
            ([TreeSpecies.OAK], SpeciesKey.SILVER_BIRCH)
        ]
        self.run_with_test_assertions(assertions, species_to_key)
        self.assertRaises(UserWarning, species_to_key, 'kissa123')
        self.assertRaises(UserWarning, species_to_key, None)

    def test_solve_hdom_key(self):
        d = {
            10: None,
            12: None,
            14: None,
            16: None,
            18: None
        }
        assertions = [
            (10, 10),
            (11, 12),
            (11.1111, 12),
            (9, 10),
            (20, 18),
        ]
        for i in assertions:
            result = solve_hdom_key(i[0], d.keys())
            self.assertEqual(i[1], result)

    def test_get_thinning_bounds(self):
        tree_variables = [
            {
                'species': 2,
                'breast_height_diameter': 10.0,
                'stems_per_ha': 100.0
            },
            {
                'species': 1,
                'breast_height_diameter': 10.0,
                'stems_per_ha': 100.0
            },
            {
                'species': 2,
                'breast_height_diameter': 10.0,
                'stems_per_ha': 100.0
            }
        ]
        stand_variables = {
            'site_type_category': 1,
            'soil_peatland_category': 1
        }
        stand = ForestStand(**stand_variables)
        stand.reference_trees = [ReferenceTree(**tv) for tv in tree_variables]

        assertions = [
            ([stand], (15.2, 24.0))
        ]
        self.run_with_test_assertions(assertions, get_thinning_bounds)


