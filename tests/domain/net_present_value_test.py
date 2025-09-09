import unittest
import lukefi.metsi.domain.data_collection.net_present_value as npv
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.collected_data import CollectedData
from lukefi.metsi.domain.collected_types import CrossCutResult, PriceableOperationInfo
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.domain.utils.file_io import get_land_values_as_dict, get_renewal_costs_as_dict

class NPVTest(unittest.TestCase):

    land_values = get_land_values_as_dict("tests/resources/net_present_value_test/land_values_per_site_type_and_interest_rate.json")
    renewal_costs = get_renewal_costs_as_dict("tests/resources/renewal_test/renewal_operation_pricing.csv")
    stand = ForestStand(
            area=10,
            soil_peatland_category=1,
            site_type_category=1,
        )

    default_rate = 3

    def test_get_bare_land_value(self):

        blv = npv._get_bare_land_value(
            self.land_values,
            soil_peatland_category = 1,
            site_type = 1,
            interest_rate = 5
            )
        self.assertEqual(blv, 332)


    def test_discount_factor(self):
        fn = npv._discount_factor
        self.assertEqual(fn(0, 0, 0), 1)
        self.assertEqual(fn(0.123, 0, 0), 1)
        self.assertEqual(fn(0, 123, 0), 1)
        self.assertAlmostEqual(fn(0.05, 20, 0), 2.6533, places=4)
        self.assertEqual(fn(0, 2022, 2022), 1)
        self.assertAlmostEqual(fn(0.05, 2025, 2020), 1.2763, places=4)



    def test_npv_of_untouched_stand_equals_bare_land_value_discounted_to_year_151(self):
        collected_data = CollectedData(
            # no operations have been done for the stand
            operation_results={},
        )
        actual = npv._calculate_npv_for_rate(self.stand, collected_data, self.land_values, self.renewal_costs, self.default_rate)
        expected = npv._get_bare_land_value(
                        self.land_values,
                        soil_peatland_category = 1,
                        site_type = 1,
                        interest_rate = self.default_rate
                        )
        self.assertAlmostEqual(actual, expected)


    def test_npv_of_cross_cut_stand_equals_the_discounted_timber_value_plus_bare_land_value(self):
        collected_data = CollectedData(
            operation_results={
                "cross_cutting": [
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=2,
                        value_per_ha=100,
                        stand_area=self.stand.area,
                        source="harvested",
                        operation="thin1",
                        time_point=5
                        )]*3
            },
            current_time_point=5
        )

        actual = npv._calculate_npv_for_rate(self.stand, collected_data, self.land_values, self.renewal_costs, self.default_rate)
        expected = 2587.826 + 2816 # discounted value of three CrossCutResults + discounted bare land value
        self.assertAlmostEqual(actual, expected, places=3)


    def test_npv_of_cross_cut_and_planted_stand_equals_the_discounted_timber_value_minus_planting_cost_plus_bare_land_value(self):
        collected_data = CollectedData(
            operation_results={
                "cross_cutting": [
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=2,
                        value_per_ha=100,
                        stand_area=self.stand.area,
                        source="harvested",
                        operation="clearcutting",
                        time_point=5
                        )]*3,
                "renewal":[
                    PriceableOperationInfo(
                        operation="scalping",
                        units=self.stand.area,
                        time_point=5
                    )]
            },
            current_time_point=5
        )

        actual = npv._calculate_npv_for_rate(self.stand, collected_data, self.land_values, self.renewal_costs, self.default_rate)
        expected = 2587.8263 - 862.6087 + 2816 # discounted value of three CrossCutResults - discounted cost of planting + discounted bare land value
        self.assertAlmostEqual(actual, expected, places=3)


    def test_calculate_npv_only_considers_standing_trees_cross_cut_results_from_the_present_time(self):
        collected_data = CollectedData(
            operation_results={
                "cross_cutting": [
                    #this 'standing_trees' result should not be considered, since it's been done at time point 0, and the current time point is 5
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=2,
                        value_per_ha=100,
                        stand_area=self.stand.area,
                        source="standing",
                        operation="",
                        time_point=0
                        ),
                    #this 'standing_trees' result should be considered, since it's been done at the current time point (5)
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=2,
                        value_per_ha=100,
                        stand_area=self.stand.area,
                        source="standing",
                        operation="",
                        time_point=5
                        )],
            },
            current_time_point=5
        )

        actual = npv._calculate_npv_for_rate(self.stand, collected_data, self.land_values, self.renewal_costs, self.default_rate)
        expected = 862.6087 + 2816 # discounted value of current stock + discounted bare land value
        self.assertAlmostEqual(actual, expected, places=3)

