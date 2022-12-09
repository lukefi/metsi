from copy import deepcopy
import unittest
from forestdatamodel.model import ForestStand
from forestry.renewal import *

from sim.core_types import AggregatedResults

class RenewalTest(unittest.TestCase):
    payload = (
        ForestStand(area=2.0), 
        AggregatedResults(current_time_point=3)
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
        new_stand, aggrs = clearing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["clearing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mechanical_clearing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mechanical_clearing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_chemical_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mechanical_chemical_clearing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mechanical_chemical_clearing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_prevention_of_aspen_saplings(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = prevention_of_aspen_saplings(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["prevention_of_aspen_saplings"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_clearing_before_cutting(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = clearing_before_cutting(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["clearing_before_cutting"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_complementary_planting(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = complementary_planting(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["complementary_planting"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_complementary_sowing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = complementary_sowing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["complementary_sowing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so
    
    def test_mechanical_hay_prevention(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mechanical_hay_prevention(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mechanical_hay_prevention"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mechanical_clearing_other_species(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mechanical_clearing_other_species"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_chemical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = chemical_clearing_other_species(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["chemical_clearing_other_species"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mechanical_chemical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mechanical_chemical_clearing_other_species(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mechanical_chemical_clearing_other_species"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_hole_clearing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = hole_clearing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["hole_clearing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_ditching(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = ditching(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["ditching"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_reconditioning_ditching(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = reconditioning_ditching(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["reconditioning_ditching"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_ditch_blocking(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = ditch_blocking(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["ditch_blocking"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_root_rot_prevention(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = root_rot_prevention(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["root_rot_prevention"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_other_regeneration(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = other_regeneration(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["other_regeneration"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_soil_preparation(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = soil_preparation(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["soil_preparation"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_scalping(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = scalping(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["scalping"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mounding_by_ground_turning(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mounding_by_ground_turning(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mounding_by_ground_turning"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_furrow_mounding(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = furrow_mounding(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["furrow_mounding"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_harrowing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = harrowing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["harrowing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_ploughing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = ploughing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["ploughing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_mounding_by_ditching(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = mounding_by_ditching(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["mounding_by_ditching"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_field_preparation(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = field_preparation(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["field_preparation"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_controlled_burning(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = controlled_burning(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["controlled_burning"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so
    
    def test_digger_scalping(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = digger_scalping(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["digger_scalping"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_soil_preparation_by_tree_stump_lifting(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = soil_preparation_by_tree_stump_lifting(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["soil_preparation_by_tree_stump_lifting"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so

    def test_cross_harrowing(self):
        payload = deepcopy(self.payload)
        new_stand, aggrs = cross_harrowing(payload, **self.operation_parameters)
        self.assertEqual(aggrs.get("renewal")["cross_harrowing"].units, self.payload[0].area)
        self.assertStandsEqual(payload[0], new_stand) # the operation should not modify the stand, thus checking that it hasn't done so
