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

    operation_parameters = {'cost_per_ha': 1000}

    def test_clearing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = clearing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["clearing"][3], 2000.0)

    def test_mechanical_clearing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mechanical_clearing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mechanical_clearing"][3], 2000.0)

    def test_mechanical_chemical_clearing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mechanical_chemical_clearing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mechanical_chemical_clearing"][3], 2000.0)

    def test_prevention_of_aspen_saplings(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = prevention_of_aspen_saplings(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["prevention_of_aspen_saplings"][3], 2000.0)

    def test_clearing_before_cutting(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = clearing_before_cutting(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["clearing_before_cutting"][3], 2000.0)

    def test_complementary_planting(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = complementary_planting(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["complementary_planting"][3], 2000.0)

    def test_complementary_sowing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = complementary_sowing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["complementary_sowing"][3], 2000.0)
    
    def test_mechanical_hay_prevention(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mechanical_hay_prevention(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mechanical_hay_prevention"][3], 2000.0)

    def test_mechanical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mechanical_clearing_other_species(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mechanical_clearing_other_species"][3], 2000.0)

    def test_chemical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = chemical_clearing_other_species(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["chemical_clearing_other_species"][3], 2000.0)

    def test_mechanical_chemical_clearing_other_species(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mechanical_chemical_clearing_other_species(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mechanical_chemical_clearing_other_species"][3], 2000.0)

    def test_hole_clearing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = hole_clearing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["hole_clearing"][3], 2000.0)

    def test_ditching(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = ditching(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["ditching"][3], 2000.0)

    def test_reconditioning_ditching(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = reconditioning_ditching(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["reconditioning_ditching"][3], 2000.0)

    def test_ditch_blocking(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = ditch_blocking(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["ditch_blocking"][3], 2000.0)

    def test_root_rot_prevention(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = root_rot_prevention(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["root_rot_prevention"][3], 2000.0)

    def test_other_regeneration(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = other_regeneration(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["other_regeneration"][3], 2000.0)

    def test_soil_preparation(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = soil_preparation(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["soil_preparation"][3], 2000.0)

    def test_scalping(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = scalping(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["scalping"][3], 2000.0)

    def test_mounding_by_ground_turning(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mounding_by_ground_turning(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mounding_by_ground_turning"][3], 2000.0)

    def test_furrow_mounding(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = furrow_mounding(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["furrow_mounding"][3], 2000.0)

    def test_harrowing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = harrowing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["harrowing"][3], 2000.0)

    def test_ploughing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = ploughing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["ploughing"][3], 2000.0)

    def test_mounding_by_ditching(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = mounding_by_ditching(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["mounding_by_ditching"][3], 2000.0)

    def test_field_preparation(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = field_preparation(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["field_preparation"][3], 2000.0)

    def test_controlled_burning(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = controlled_burning(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["controlled_burning"][3], 2000.0)
    
    def test_digger_scalping(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = digger_scalping(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["digger_scalping"][3], 2000.0)

    def test_soil_preparation_by_tree_stump_lifting(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = soil_preparation_by_tree_stump_lifting(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["soil_preparation_by_tree_stump_lifting"][3], 2000.0)

    def test_cross_harrowing(self):
        payload = deepcopy(self.payload)
        op_params = deepcopy(self.operation_parameters)
        _, aggrs = cross_harrowing(payload, **op_params)
        self.assertEqual(aggrs.get("renewal")["cross_harrowing"][3], 2000.0)
