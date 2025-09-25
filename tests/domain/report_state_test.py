import unittest
from lukefi.metsi.domain.collected_types import CrossCutResult
from lukefi.metsi.sim.collected_data import CollectedData
from lukefi.metsi.domain.data_collection.marshalling import report_period, report_state
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.data.enums.internal import TreeSpecies
from types import SimpleNamespace

class ReportStateTest(unittest.TestCase):

    def test_report_state_considers_only_current_time_point(self):
        collected_data = CollectedData(
            treatment_results={
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

        _, collected_data = report_state((ForestStand(), collected_data), **collectives)
        self.assertEqual(collected_data.operation_results["report_state"][1]["cross_cut_volume"], 1)



    def test_report_state_can_read_reference_trees(self):
        stand = ForestStand(
            reference_trees = [
                ReferenceTree(species = TreeSpecies.SPRUCE, stems_per_ha = 10),
                ReferenceTree(species = TreeSpecies.SPRUCE, stems_per_ha = 10),
                ReferenceTree(species = TreeSpecies.PINE, stems_per_ha = 1),
                ]
        )
        collected_data = CollectedData(current_time_point=2)

        collectives = {
         "spruce_per_ha": 'reference_trees.stems_per_ha[reference_trees.species == 2]'
        }

        _, collected_data = report_state((stand, collected_data), **collectives)
        self.assertEqual(collected_data.operation_results["report_state"][2]["spruce_per_ha"], 20)


    def test_report_period(self):
        """ Test suite for reporting a period
        Test setup is as follows:
        We are accumulating the variable a in operX at time points 10 and 20
        """
        collected_data = CollectedData(
            treatment_results={
                'operX': [
                    SimpleNamespace(
                        a=10,
                        time_point=5
                    ),
                    SimpleNamespace(
                        a=30,
                        time_point=5
                    ),
                    SimpleNamespace(
                        a=100,
                        time_point=15
                    )
                ]
            }
        )
        collectives = {
            'accumulate_a': 'operX.a'
        }
        # period reporting for years 0-9
        collected_data.current_time_point = 10
        res = report_period((None, collected_data), **collectives)
        self.assertEqual(res[1].operation_results['report_period'][collected_data.current_time_point]['accumulate_a'], 40)
        # period for years 10-19
        collected_data.current_time_point = 20
        res = report_period((None, collected_data), **collectives)
        self.assertEqual(res[1].operation_results['report_period'][collected_data.current_time_point]['accumulate_a'], 100)
