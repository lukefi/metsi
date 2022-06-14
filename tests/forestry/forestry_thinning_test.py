import unittest
from collections import OrderedDict
from tests.test_utils import ConverterTestSuite
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestry.thinning_limits import *
from forestry.thinning import thinning_from_below, thinning_from_above, report_overall_removal
import forestry.aggregate_utils as aggutil

class ThinningsTest(ConverterTestSuite):

    def test_thinning_from_above(self):
        species = [ TreeSpecies(i) for i in [1,2,3] ]
        diameters = [ 20.0 + i for i in range(0, 3) ]
        stems = [ 200.0 + i for i in range(0, 3) ]

        stand = ForestStand()
        stand.site_type_category = 1
        stand.soil_peatland_category = 1
        stand.reference_trees = [
            ReferenceTree(species=s, breast_height_diameter=d, stems_per_ha=f)
            for s, d, f in zip(species, diameters, stems)
        ]

        operation_tag = 'thinning_from_above'
        simulation_aggregates = {
            'operation_results': {},
            'current_time_point': 0,
            'current_operation_tag': operation_tag
        }
        operation_parameters = {'c': 0.97, 'e': 0.2}

        oper_input = (stand, simulation_aggregates)
        result_stand, collected_aggregates = thinning_from_above(oper_input, **operation_parameters)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertEqual([22.0, 21.0, 20.0], [rt.breast_height_diameter for rt in stand.reference_trees])
        self.assertEqual(124.0792, round(result_stand.reference_trees[0].stems_per_ha, 4))
        self.assertEqual(145.4833, round(result_stand.reference_trees[1].stems_per_ha, 4))
        self.assertEqual(170.2916, round(result_stand.reference_trees[2].stems_per_ha, 4))
        self.assertEqual(163.1459, round(list(collected_aggregates['operation_results'][operation_tag].values())[-1]['stems_removed'], 4))

    def test_thinning_from_below(self):
        species = [ TreeSpecies(i) for i in [1,2,3] ]
        diameters = [ 20.0 + i for i in range(0, 3) ]
        stems = [ 200.0 + i for i in range(0, 3) ]

        stand = ForestStand()
        stand.site_type_category = 1
        stand.soil_peatland_category = 1
        stand.reference_trees = [
            ReferenceTree(species=s, breast_height_diameter=d, stems_per_ha=f)
            for s, d, f in zip(species, diameters, stems)
        ]

        simulation_aggregates = {
            'operation_results': {},
            'current_time_point': 0,
            'current_operation_tag': 'thinning_from_below'
        }
        operation_parameters = {'c': 0.97, 'e': 0.2}

        oper_input = (stand, simulation_aggregates)
        result_stand, collected_aggregates = thinning_from_below(oper_input, **operation_parameters)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertEqual([20.0, 21.0, 22.0], [rt.breast_height_diameter for rt in stand.reference_trees])
        self.assertEqual(119.1652, round(result_stand.reference_trees[0].stems_per_ha, 4))
        self.assertEqual(142.5737, round(result_stand.reference_trees[1].stems_per_ha, 4))
        self.assertEqual(170.2745, round(result_stand.reference_trees[2].stems_per_ha, 4))
        self.assertEqual(170.9866, round(list(collected_aggregates['operation_results']['thinning_from_below'].values())[-1]['stems_removed'], 4))

    def test_report_overall_removal(self):
        operation_results = {
            'thin1': OrderedDict({
                        0: { 'stems_removed': 100 }
                    }),
            'thin2': OrderedDict({
                        0: { 'stems_removed': 200 },
                        15: { 'stems_removed': 300 }
                    })
        }
        simulation_aggregates = {
            'operation_results': operation_results,
            'current_time_point': 30,
        }
        payload = (None, simulation_aggregates)
        (_, result) = report_overall_removal(payload, thinning_method=['thin1', 'thin2'])
        overall_removals = aggutil.get_latest_operation_aggregate(result, 'report_overall_removal')
        overall_removal = sum(x for x in overall_removals.values())
        self.assertEqual(600, overall_removal)

class ThinningLimitsTest(ConverterTestSuite):
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
        hdoms = {
            10: None,
            12: None,
            14: None,
            16: None,
            18: None
        }
        assertions = [
            (9, 10),
            (10, 12),
            (11, 12),
            (14, 16),
            (14.11111, 16),
            (17, 18),
            (18, 18),
            (20, 18),
        ]
        for i in assertions:
            result = solve_hdom_key(i[0], hdoms.keys())
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


