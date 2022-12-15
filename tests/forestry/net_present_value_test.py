import unittest
import forestry.net_present_value as npv
from forestdatamodel.model import ForestStand
from sim.core_types import AggregatedResults
from forestry.cross_cutting import CrossCutResult
from forestry.renewal import PriceableOperationInfo
from forestdatamodel.enums.internal import TreeSpecies

class NPVTest(unittest.TestCase):

    def test_get_bare_land_value(self):
        blv = npv._get_bare_land_value(
            "tests/resources/net_present_value_test/land_values_per_site_type_and_interest_rate.json", 
            soil_peatland_category = 1,
            site_type = 1, 
            interest_rate = 0.05
            )
        self.assertEqual(blv, 332)


    def test_discount_factor(self):
        fn = npv._discount_factor
        self.assertEqual(fn(0, 0), 1)
        self.assertEqual(fn(0.123, 0), 1)
        self.assertEqual(fn(0, 123), 1)
        self.assertAlmostEqual(fn(0.05, 20), 2.6533, places=4)


    def test_npv_of_untouched_stand_equals_bare_land_value_discounted_to_year_151(self):
        stand = ForestStand(
            soil_peatland_category=1,
            site_type_category=1,
        )

        aggrs = AggregatedResults(
            # no operations have been done for the stand
            operation_results={},
        )
        
        interest_rate = 0.01
        operation_parameters = {
            "interest_rates": [interest_rate],
            "land_values": "tests/resources/net_present_value_test/land_values_per_site_type_and_interest_rate.json",
            "renewal_costs": "tests/resources/renewal_test/renewal_operation_pricing.csv",
        }

        stand, new_aggrs = npv.calculate_npv((stand, aggrs), **operation_parameters)
        actual = new_aggrs.get("net_present_value")[new_aggrs.current_time_point][str(interest_rate)]
        expected = npv._get_bare_land_value(
                        "tests/resources/net_present_value_test/land_values_per_site_type_and_interest_rate.json", 
                        soil_peatland_category = 1,
                        site_type = 1, 
                        interest_rate = interest_rate
                        )
        self.assertAlmostEqual(actual, expected)


    def test_npv_of_cross_cut_stand_equals_the_discounted_timber_value_plus_bare_land_value(self):
        stand = ForestStand(
            area=10,
            soil_peatland_category=1,
            site_type_category=1,
        )

        interest_rate = 0.03

        aggrs = AggregatedResults(
            operation_results={
                "cross_cutting": [
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=2,
                        value_per_ha=100, 
                        stand_area=stand.area,
                        source="thin1",
                        time_point=5
                        )]*3
            },
        )

        operation_parameters = {
            "interest_rates": [interest_rate],
            "land_values": "tests/resources/net_present_value_test/land_values_per_site_type_and_interest_rate.json",
            "renewal_costs": "tests/resources/renewal_test/renewal_operation_pricing.csv",
        }

        stand, new_aggrs = npv.calculate_npv((stand, aggrs), **operation_parameters)
        actual = new_aggrs.get("net_present_value")[new_aggrs.current_time_point].get(str(interest_rate))
        expected = 2587.826 + 2816 # discounted value of three CrossCutResults + discounted bare land value
        self.assertAlmostEqual(actual, expected, places=3)

    def test_npv_of_cross_cut_and_planted_stand_equals_the_discounted_timber_value_minus_planting_cost_plus_bare_land_value(self):
        stand = ForestStand(
            area=10,
            soil_peatland_category=1,
            site_type_category=1,
        )

        interest_rate = 0.03

        aggrs = AggregatedResults(
            operation_results={
                "cross_cutting": [
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=2,
                        value_per_ha=100, 
                        stand_area=stand.area,
                        source="clearcutting",
                        time_point=5
                        )]*3,
                "renewal":[
                    PriceableOperationInfo(
                        operation_name="scalping",
                        units=stand.area,
                        time_point=5
                    )]
            },
        )

        operation_parameters = {
            "interest_rates": [interest_rate],
            "land_values": "tests/resources/net_present_value_test/land_values_per_site_type_and_interest_rate.json",
            "renewal_costs": "tests/resources/renewal_test/renewal_operation_pricing.csv",
        }

        stand, new_aggrs = npv.calculate_npv((stand, aggrs), **operation_parameters)
        actual = new_aggrs.get("net_present_value")[new_aggrs.current_time_point].get(str(interest_rate))
        expected = 2587.8263 - 862.6087 + 2816 # discounted value of three CrossCutResults - discounted cost of planting + discounted bare land value
        self.assertAlmostEqual(actual, expected, places=3)


