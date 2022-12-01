from forestry.cross_cutting import CrossCuttableTree
from tests.test_utils import ConverterTestSuite, get_default_timber_price_table
from forestryfunctions.cross_cutting.model import CrossCuttableTree
from forestdatamodel.model import ReferenceTree
from forestry.thinning_limits import *
from sim.core_types import AggregatedResults
import forestry.thinning as thin
import numpy as np
from forestry.utils import get_timber_price_table

class ThinningsTest(ConverterTestSuite):

    def test_evaluate_thinning_conditions(self):
        assertions = [
            (1, False),
            (2, False),
            (3, True),
            (4, False),
            (5, False),
        ]
        for i in assertions:
            p1 = lambda: i[0] < 5
            p2 = lambda: i[0] == 3
            predicates = [p1, p2]
            result = thin.evaluate_thinning_conditions(predicates)
            self.assertEqual(i[1], result)

    def test_first_thinning(self):
        species = [TreeSpecies(i) for i in [1, 2, 2]]
        diameters = [12.0, 16.0, 12.0]
        stems = [300, 600, 200]
        heights = [10.0, 15.0, 10.0]

        stand = ForestStand()
        stand.site_type_category = 1
        stand.reference_trees = [
            ReferenceTree(species=spe, breast_height_diameter=d, stems_per_ha=f, height=h)
            for spe, d, f, h in zip(species, diameters, stems, heights)
        ]
        operation_tag = 'first_thinning'
        simulation_aggregates = AggregatedResults()
        operation_parameters = {
            'thinning_factor': 0.97,
            'e': 10,
            'dominant_height_lower_bound': 11,
            'dominant_height_upper_bound': 16,
            'timber_price_table': get_default_timber_price_table()
        }
        payload = (stand, simulation_aggregates)
        result_stand, collected_aggregates = thin.first_thinning(payload, **operation_parameters)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertAlmostEqual(257.6202, result_stand.reference_trees[0].stems_per_ha, places=4)
        self.assertAlmostEqual(180.7842, result_stand.reference_trees[1].stems_per_ha, places=4)
        self.assertAlmostEqual(570.594, result_stand.reference_trees[2].stems_per_ha, places=4)
        self.assertAlmostEqual(600-570.594, collected_aggregates.get_list_result("felled_trees")[-1].stems_to_cut_per_ha, places=4)


    def test_thinning_from_above(self):
        species = [TreeSpecies(i) for i in [1, 2, 3]]
        diameters = [20.0 + i for i in range(0, 3)]
        stems = [200.0 + i for i in range(0, 3)]
        heights = [20.0 + i for i in range(0, 3)]

        stand = ForestStand()
        stand.site_type_category = 1
        stand.soil_peatland_category = 1
        stand.reference_trees = [
            ReferenceTree(species=s, breast_height_diameter=d, stems_per_ha=f, height=h)
            for s, d, f, h in zip(species, diameters, stems, heights)
        ]

        operation_tag = 'thinning_from_above'
        simulation_aggregates = AggregatedResults()
        operation_parameters = {
            'thinning_factor': 0.97, 
            'e': 0.2,
            'timber_price_table': get_default_timber_price_table()}

        oper_input = (stand, simulation_aggregates)
        result_stand, collected_aggregates = thin.thinning_from_above(oper_input, **operation_parameters)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertEqual([22.0, 21.0, 20.0], [rt.breast_height_diameter for rt in stand.reference_trees])
        self.assertAlmostEqual(124.0792, result_stand.reference_trees[0].stems_per_ha, places=4)
        self.assertAlmostEqual(145.4833, result_stand.reference_trees[1].stems_per_ha, places=4)
        self.assertAlmostEqual(170.2916, result_stand.reference_trees[2].stems_per_ha, places=4)
        self.assertAlmostEqual(200-170.2916, collected_aggregates.get_list_result("felled_trees")[-1].stems_to_cut_per_ha, places=4)

    def test_thinning_from_below(self):
        species = [TreeSpecies(i) for i in [1, 2, 3]]
        diameters = [20.0 + i for i in range(0, 3)]
        stems = [200.0 + i for i in range(0, 3)]
        heights = [20.0 + i for i in range(0, 3)]

        stand = ForestStand()
        stand.site_type_category = 1
        stand.soil_peatland_category = 1
        stand.reference_trees = [
            ReferenceTree(species=s, breast_height_diameter=d, stems_per_ha=f, height=h)
            for s, d, f, h in zip(species, diameters, stems, heights)
        ]

        simulation_aggregates = AggregatedResults()
        operation_parameters = {
            'thinning_factor': 0.97, 
            'e': 0.2,
            'timber_price_table': get_default_timber_price_table()
            }

        oper_input = (stand, simulation_aggregates)
        result_stand, collected_aggregates = thin.thinning_from_below(oper_input, **operation_parameters)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertEqual([20.0, 21.0, 22.0], [rt.breast_height_diameter for rt in stand.reference_trees])
        self.assertAlmostEqual(119.1652, result_stand.reference_trees[0].stems_per_ha, places=4)
        self.assertAlmostEqual(142.5737, result_stand.reference_trees[1].stems_per_ha, places=4)
        self.assertAlmostEqual(170.2745, result_stand.reference_trees[2].stems_per_ha, places=4)
        self.assertAlmostEqual(202-170.2745, collected_aggregates.get_list_result("felled_trees")[-1].stems_to_cut_per_ha, places=4)

    def test_even_thinning(self):
        species = [TreeSpecies(i) for i in [1, 2, 3]]
        diameters = [20.0 + i for i in range(0, 3)]
        stems = [200.0 + i for i in range(0, 3)]
        heights = [20.0 + i for i in range(0, 3)]

        stand = ForestStand()
        stand.site_type_category = 1
        stand.soil_peatland_category = 1
        stand.reference_trees = [
            ReferenceTree(species=s, breast_height_diameter=d, stems_per_ha=f, height=h)
            for s, d, f, h in zip(species, diameters, stems, heights)
        ]

        simulation_aggregates = AggregatedResults()
        operation_parameters = {
            'thinning_factor': 0.50, 
            'e': 0.2,
            'timber_price_table': get_default_timber_price_table()
            }

        oper_input = (stand, simulation_aggregates)
        result_stand, collected_aggregates = thin.even_thinning(oper_input, **operation_parameters)
        self.assertEqual(3, len(result_stand.reference_trees))
        self.assertEqual([20.0, 21.0, 22.0], [rt.breast_height_diameter for rt in stand.reference_trees])
        self.assertAlmostEqual(100.0, result_stand.reference_trees[0].stems_per_ha, places=4)
        self.assertAlmostEqual(100.5, result_stand.reference_trees[1].stems_per_ha, places=4)
        self.assertAlmostEqual(101.0, result_stand.reference_trees[2].stems_per_ha, places=4)
        self.assertAlmostEqual(202-101.0, collected_aggregates.get_list_result("felled_trees")[-1].stems_to_cut_per_ha, places=4)

    def test_report_overall_removal(self):
        operation_results = {
            "felled_trees":[
                    CrossCuttableTree(
                        stems_to_cut_per_ha=100,
                        species=TreeSpecies.PINE,
                        breast_height_diameter=0,
                        height=0,
                        source="thin1",
                        time_point=0
                    ),
                    CrossCuttableTree(
                        stems_to_cut_per_ha=200,
                        species=TreeSpecies.PINE,
                        breast_height_diameter=0,
                        height=0,
                        source="thin2",
                        time_point=0
                    ),
                    CrossCuttableTree(
                        stems_to_cut_per_ha=300,
                        species=TreeSpecies.PINE,
                        breast_height_diameter=0,
                        height=0,
                        source="thin2",
                        time_point=15
                    ),
            ]
        }

        simulation_aggregates = AggregatedResults(
            operation_results = operation_results,
            current_time_point = 30
        )
        payload = (None, simulation_aggregates)
        (_, result) = thin.report_overall_removal(payload, thinning_method=['thin1', 'thin2'])
        overall_removals = result.prev('report_overall_removal')
        overall_removal = sum(x for x in overall_removals.values())
        self.assertEqual(600, overall_removal)


class ThinningLimitsTest(ConverterTestSuite):

    def test_get_first_thinning_residue(self):
        stand = ForestStand()
        stand.site_type_category = 1
        species = [TreeSpecies(i) for i in [1, 2, 2]]
        diameters = [12.0, 16.0, 12.0]
        stems = [450.0, 600.0, 500.0]
        stand.reference_trees = [
            ReferenceTree(species=spe, breast_height_diameter=d, stems_per_ha=f)
            for spe, d, f in zip(species, diameters, stems)
        ]
        result = resolve_first_thinning_residue(stand)
        residue_stems = 1000.0
        self.assertEqual(residue_stems, result)

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

    # def read_thinning_limits_file(self):
    #     return open('tests/resources/thinning_limits.txt', 'r').read()

    def test_create_thinning_limits_table(self):
        # thinning_limits = open('tests/resources/thinning_limits.txt', 'r').read()
        table = create_thinning_limits_table('tests/resources/thinning_limits.txt')
        self.assertEqual(len(table), 64)
        self.assertEqual(len(table[0]), 9)

    def test_get_thinning_limits_from_parameter_file_contents(self):
        thinning_limits = 'tests/resources/thinning_limits.txt'

        kwarg_dicts = [
            {
             "thinning_limits_file": thinning_limits,
             "county": CountyKey.EASTERN_FINLAND,
             "sp_category": SoilPeatlandKey.MINERAL_SOIL,
             "site_type": SiteTypeKey.OMT,
             "species": SpeciesKey.PINE
            },
            {
             "thinning_limits_file": thinning_limits,
             "county": CountyKey.EASTERN_FINLAND,
             "sp_category": SoilPeatlandKey.PEATLAND,
             "site_type": SiteTypeKey.MT,
             "species": SpeciesKey.DOWNY_BIRCH
            }
        ]

        limits0 = get_thinning_limits_from_parameter_file_contents(**kwarg_dicts[0])
        self.assertEqual(limits0[10], (15.3, 24.0))

        limits1 = get_thinning_limits_from_parameter_file_contents(**kwarg_dicts[1])
        self.assertEqual(limits1[10], (10.4, 14.0))

    def test_get_thinning_bounds(self):
        tree_variables = [
            {
                'species': TreeSpecies.SPRUCE,
                'breast_height_diameter': 10.0,
                'stems_per_ha': 100.0
            },
            {
                'species': TreeSpecies.PINE,
                'breast_height_diameter': 10.0,
                'stems_per_ha': 100.0
            },
            {
                'species': TreeSpecies.SPRUCE,
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
        stand2 = ForestStand(reference_trees=[], **stand_variables)

        thinning_limits = 'tests/resources/thinning_limits.txt'

        assertions = [
            ([stand], (15.2, 24.0)),
            ([stand, thinning_limits], (15.2, 24.0)),  # uses thinning_limits.txt as the source for thinning limits
        ]
        self.run_with_test_assertions(assertions, resolve_thinning_bounds)
        self.assertRaises(UserWarning, resolve_thinning_bounds, *[stand2, thinning_limits])

    def test_get_timber_price_table(self):
        thinning_limits_file = 'tests/resources/timber_price_table.csv'
        actual = get_timber_price_table(thinning_limits_file)

        expected = np.array(
                           [[  1., 160., 370.,  55.],
                            [  1., 160., 400.,  57.],
                            [  1., 160., 430.,  59.],
                            [  1., 160., 460.,  59.],
                            [  2.,  70., 300.,  17.]])

        self.assertTrue(np.array_equal(expected, actual))
