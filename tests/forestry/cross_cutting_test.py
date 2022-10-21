import unittest
from forestry.cross_cutting import cross_cut_whole_stand, cross_cut_thinning_output
from sim.core_types import AggregatedResults
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from tests.test_utils import get_default_timber_price_table
from forestryfunctions.cross_cutting.model import CrossCuttableTrees, CrossCuttableTree, CrossCutResults

class CrossCuttingTest(unittest.TestCase):
    
    def test_cross_cut_thinning_output_cross_cuts_only_once(self):
        """
        First CrossCuttableTrees object has already been cross cut, but the second one has not been cross cut yet.
        The operation should only cross cut the second one.
        """
        payload = (
            ForestStand(area=2.0), 
            AggregatedResults(
                operation_results={
                    "thinning_from_below":{
                        10: CrossCuttableTrees(
                                trees = [CrossCuttableTree(
                                    stems_to_cut_per_ha = 0.006261167484111818,
                                    species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                    breast_height_diameter = 15.57254199723247,
                                    height = 18.293846547993535,
                            )],
                            cross_cut_done=True
                        ),
                        20: CrossCuttableTrees(
                                trees = [CrossCuttableTree(
                                    stems_to_cut_per_ha = 0.006261167484111818,
                                    species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                    breast_height_diameter = 15.57254199723247,
                                    height = 18.293846547993535,
                            )],
                            cross_cut_done=False
                        ),
                    }
                }
            )
        )

        timber_price_table_str = get_default_timber_price_table()
        operation_parameters = {'timber_price_table': timber_price_table_str}

        _, aggrs = cross_cut_thinning_output(payload, **operation_parameters)
        res = aggrs.get("thinned_trees_cross_cut")["thinning_from_below"]
        self.assertEqual(res.keys(), {20})
        self.assertEqual(len(res[20].results), 2)
        self.assertEqual(aggrs.get('thinning_from_below')[10].cross_cut_done, True)


    def test_cross_cut_whole_stand(self):
        #stand with three reference trees
        stand = ForestStand(
            area=2.0,
            reference_trees=[
                ReferenceTree(
                    species=TreeSpecies.UNKNOWN_CONIFEROUS,
                    breast_height_diameter=15.57254199723247,
                    height=18.293846547993535,
                    stems_per_ha=0.006261167484111818,
                ),
                ReferenceTree(
                    species=TreeSpecies.UNKNOWN_CONIFEROUS,
                    breast_height_diameter=15.57254199723247,
                    height=18.293846547993535,
                    stems_per_ha=0.006261167484111818,
                ),
                ReferenceTree(
                    species=TreeSpecies.UNKNOWN_CONIFEROUS,
                    breast_height_diameter=15.57254199723247,
                    height=18.293846547993535,
                    stems_per_ha=0.006261167484111818,
                ),
            ]
        )
        payload = (stand, AggregatedResults())

        timber_price_table_str = get_default_timber_price_table()
        operation_parameters = {'timber_price_table': timber_price_table_str}

        _, aggrs = cross_cut_whole_stand(payload, **operation_parameters)
        res = aggrs.get("standing_trees_cross_cut")
        self.assertEqual(len(res[0]), 6)

