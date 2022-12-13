import unittest
from forestry.cross_cutting import CrossCutResult
from sim.core_types import AggregatedResults
from forestry.operations import report_state
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies

class ReportStateTest(unittest.TestCase):
    
    def test_report_state_considers_only_current_time_point(self):
        aggr = AggregatedResults(
            operation_results={
                "cross_cutting": [
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=0.5,
                        value_per_ha=2,
                        stand_area=1,
                        source="harvested",
                        operation="thinning_from_above",
                        time_point=1
                    ),
                    CrossCutResult(
                        species=TreeSpecies.PINE,
                        timber_grade=1,
                        volume_per_ha=0.5,
                        value_per_ha=2,
                        stand_area=1,
                        source="harvested",
                        operation="thinning_from_above",
                        time_point=1
                    ),
                ]
            },
            current_time_point=1
        )

        collectives = {
         "cross_cut_volume": 'cross_cutting.volume_per_ha'
        }
        
        _, aggrs = report_state((ForestStand(), aggr), **collectives)
        self.assertEqual(aggrs.operation_results["report_state"][1]["cross_cut_volume"], 1)

    

    def test_report_state_can_read_reference_trees(self):
        stand = ForestStand(
            reference_trees = [
                ReferenceTree(species = TreeSpecies.SPRUCE, stems_per_ha = 10),
                ReferenceTree(species = TreeSpecies.SPRUCE, stems_per_ha = 10),
                ReferenceTree(species = TreeSpecies.PINE, stems_per_ha = 1),
                ]
        )
        aggr = AggregatedResults(current_time_point=2)

        collectives = {
         "spruce_per_ha": 'reference_trees.stems_per_ha[reference_trees.species == 2]'
        }
        
        _, aggrs = report_state((stand, aggr), **collectives)
        self.assertEqual(aggrs.operation_results["report_state"][2]["spruce_per_ha"], 20)

