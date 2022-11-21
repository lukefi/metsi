import unittest
from forestry.cross_cutting import cross_cut_whole_stand, cross_cut_felled_trees
from sim.core_types import AggregatedResults
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions.cross_cutting.model import CrossCuttableTrees, CrossCuttableTree

class CrossCuttingTest(unittest.TestCase):
    
    def test_cross_cut_thinning_output_cross_cuts_only_uncut_trees(self):
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

        operation_parameters = {'timber_price_table': "tests/resources/timber_price_table.csv"}

        _, aggrs = cross_cut_felled_trees(payload, **operation_parameters)
        res = aggrs.get("cross_cutting")["thinning_from_below"]
        self.assertEqual(res.keys(), {20})
        self.assertEqual(len(res[20].results), 2)
        self.assertEqual(aggrs.get('thinning_from_below')[10].cross_cut_done, True)


    def test_cross_cut_thinning_output_called_twice(self):
        """
        This test simulates the case when first some thinning results are produced, and cross cutting is done on them.
        Then, some more thinning results are produced, and cross cutting is called again.
        The thinned_trees_cross_cut -result under operation_results should contain the results of both cross cut operations.
        """

        operation_parameters = {'timber_price_table': "tests/resources/timber_price_table.csv"}

        payload = (
            ForestStand(area=2.0), 
            AggregatedResults(
                operation_results={
                    "thinning_from_below":{
                        20: CrossCuttableTrees(
                                trees = [CrossCuttableTree(
                                    stems_to_cut_per_ha = 0.006261167484111818,
                                    species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                    breast_height_diameter = 15.57254199723247,
                                    height = 18.293846547993535,
                            )],
                            cross_cut_done=False
                        ),
                    },
                }
            )
        )

        stand, aggrs = cross_cut_felled_trees(payload, **operation_parameters)
        res = aggrs.get("cross_cutting")["thinning_from_below"]
        self.assertEqual(res.keys(), {20})
        self.assertEqual(len(res[20].results), 2)

        # after the first cross cutting (above), add new thinning results, which need to be cross cut
        aggrs.operation_results["thinning_from_below"][30] = CrossCuttableTrees(
            trees = [CrossCuttableTree(
                stems_to_cut_per_ha = 0.006261167484111818,
                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                breast_height_diameter = 15.57254199723247,
                height = 18.293846547993535,
        )],
            cross_cut_done=False
        )

        payload = (stand, aggrs)

        _, aggrs = cross_cut_felled_trees(payload, **operation_parameters)
        res = aggrs.get("cross_cutting")["thinning_from_below"]
        # test that the results of both cross cut operations are in thinned_trees_cross_cut
        self.assertEqual(res.keys(), {20, 30})
        self.assertEqual(len(res[30].results), 2)


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

        operation_parameters = {'timber_price_table': 'tests/resources/timber_price_table.csv'}

        new_stand, aggrs = cross_cut_whole_stand(payload, **operation_parameters)
        res = aggrs.get("cross_cutting")["standing_trees"]
        self.assertEqual(len(res[0].results), 6)
        
        # test that cross_cut_whole_stand has not modified the trees
        self.assertEqual(
            [rt.stems_per_ha for rt in stand.reference_trees], 
            [rt.stems_per_ha for rt in new_stand.reference_trees]
            )


    def test_cross_cut_whole_stand_called_twice(self):
        """
        This test simulates the case when the value of a stand is calculated in two different time points.
        """
        stand = ForestStand(
            area=2.0,
            reference_trees=[
                ReferenceTree(
                    species=TreeSpecies.UNKNOWN_CONIFEROUS,
                    breast_height_diameter=15.57,
                    height=18.29,
                    stems_per_ha=0.0062,
                ),
            ]
        )
        payload = (stand, AggregatedResults(current_time_point=1))

        operation_parameters = {'timber_price_table': 'tests/resources/timber_price_table.csv'}

        stand, aggrs = cross_cut_whole_stand(payload, **operation_parameters)
        aggrs.current_time_point=2
        _, aggrs = cross_cut_whole_stand((stand, aggrs), **operation_parameters)
        res = aggrs.get("cross_cutting")["standing_trees"]
        self.assertEqual(2, len(res.keys()))