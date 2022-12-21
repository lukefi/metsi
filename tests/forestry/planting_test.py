
import unittest
from forestdatamodel.model import ForestStand
from forestdatamodel.enums.internal import TreeSpecies
from sim.core_types import AggregatedResults
import forestry.planting as plnt 
from forestry.utils.enums import SoilPreparationKey

class PlantingTest(unittest.TestCase):
    def test_plant(self):
        stand = ForestStand()
        simulation_aggregates = AggregatedResults()
        stand.site_type_category = 3
        stand.identifier = '1001'
        regen = plnt.get_planting_instructions(stand.site_type_category, 'tests/resources/planting_test/planting_instructions.txt')
        (stand, output) = plnt.plant(stand,simulation_aggregates, "regeneration",regen_species = TreeSpecies(regen['species']), rt_count = 10, rt_stems= regen['stems/ha'],
            soil_preparation=regen['soil preparation'])
        self.assertEqual(200,stand.reference_trees[-1].stems_per_ha)
        self.assertEqual(SoilPreparationKey.PATCH_MOUNDING, output.prev("regeneration")['soil preparation'])
        self.assertEqual(TreeSpecies.PINE, output.prev("regeneration")['species'])
        self.assertEqual('1001-9-tree', stand.reference_trees[-1].identifier)

    def test_planting(self):
        stand = ForestStand()
        simulation_aggregates = AggregatedResults()
        oper_input = (stand, simulation_aggregates)
        operation_parameters = {'planting_instructions':'tests/resources/planting_test/planting_instructions.txt'}
        stand.site_type_category = 4
        stand.identifier = '1011'
        (stand, output) = plnt.planting(oper_input, **operation_parameters)
        self.assertEqual(200, stand.reference_trees[-1].stems_per_ha)
        self.assertEqual(SoilPreparationKey.SCALPING, output.prev("regeneration")['soil preparation'])
        self.assertEqual(TreeSpecies.PINE, output.prev("regeneration")['species'])
        self.assertEqual('1011-9-tree', stand.reference_trees[-1].identifier)
        self.assertEqual(output.get_list_result("renewal")[-1].operation, "planting")
        self.assertEqual(output.get_list_result("renewal")[-1].units, stand.area)
        self.assertEqual(output.get_list_result("renewal")[-1].time_point, simulation_aggregates.current_time_point)

