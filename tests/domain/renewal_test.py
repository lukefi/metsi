from copy import deepcopy
import unittest
from lukefi.metsi.domain.forestry_operations.renewal import *

from lukefi.metsi.sim.collected_data import CollectedData

class RenewalTest(unittest.TestCase):
    payload = (
        ForestStand(area=2.0),
        CollectedData(current_time_point=3)
    )
    operation_parameters = {}

    def assertStandsEqual(self, stand1: ForestStand, stand2: ForestStand):
        """
        Test that stand1 and stand2 are equal.
        It performs a sort of "deep diff" for the stands, relying on the fact that only reference_trees and tree_strata are (lists of) complex objects in the stand.
        Objects are cast to dicts to avoid using the overridden __eq__ methods of the respective classes.
        """
        for t in range(len(stand1.reference_trees)):
            trees_expected = stand1.reference_trees[t].__dict__
            trees_actual = stand2.reference_trees[t].__dict__
            self.assertTrue(trees_expected == trees_actual)

        for s in range(len(stand1.tree_strata)):
            strata_expected = stand1.tree_strata[s].__dict__
            strata_actual = stand2.tree_strata[s].__dict__
            self.assertTrue(strata_expected == strata_actual)

        stands_expected = stand1.__dict__
        stands_actual = stand2.__dict__
        self.assertTrue(stands_expected == stands_actual)

    def test_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = clearing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mechanical_clearing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_chemical_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mechanical_chemical_clearing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_prevention_of_aspen_saplings(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = prevention_of_aspen_saplings(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_clearing_before_cutting(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = clearing_before_cutting(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_complementary_planting(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = complementary_planting(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_complementary_sowing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = complementary_sowing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_hay_prevention(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mechanical_hay_prevention(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mechanical_clearing_other_species(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_chemical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = chemical_clearing_other_species(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_chemical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mechanical_chemical_clearing_other_species(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_hole_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = hole_clearing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_ditching(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = ditching(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_reconditioning_ditching(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = reconditioning_ditching(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_ditch_blocking(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = ditch_blocking(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_root_rot_prevention(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = root_rot_prevention(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_other_regeneration(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = other_regeneration(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_soil_preparation(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = soil_preparation(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_scalping(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = scalping(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mounding_by_ground_turning(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mounding_by_ground_turning(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_furrow_mounding(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = furrow_mounding(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_harrowing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = harrowing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_ploughing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = ploughing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mounding_by_ditching(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = mounding_by_ditching(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_field_preparation(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = field_preparation(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_controlled_burning(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = controlled_burning(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_digger_scalping(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = digger_scalping(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_soil_preparation_by_tree_stump_lifting(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = soil_preparation_by_tree_stump_lifting(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_cross_harrowing(self):
        payload = deepcopy(self.payload)
        new_stand, collected_data = cross_harrowing(payload, **self.operation_parameters)
        self.assertEqual(collected_data.get_list_result("renewal")[0].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so
