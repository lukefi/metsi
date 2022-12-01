import unittest
from forestry.cross_cutting import CrossCutResult, CrossCuttableTree, cross_cut_standing_trees, cross_cut_felled_trees, cross_cut_tree, cross_cuttable_trees_from_stand
from sim.core_types import AggregatedResults
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from test_utils import DEFAULT_TIMBER_PRICE_TABLE, TIMBER_PRICE_TABLE_THREE_GRADES

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
                    "felled_trees": [
                        CrossCuttableTree(
                                stems_to_cut_per_ha = 0.006261167484111818,
                                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                breast_height_diameter = 15.57254199723247,
                                height = 18.293846547993535,
                                source = "thinning_from_below",
                                time_point=10,
                                cross_cut_done=True
                        ),
                        CrossCuttableTree(
                                stems_to_cut_per_ha = 0.006261167484111818,
                                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                breast_height_diameter = 15.57254199723247,
                                height = 18.293846547993535,
                                source = "thinning_from_below",
                                time_point=20,
                                cross_cut_done=False
                        )
                    ]
                }
            )
        )

        operation_parameters = {'timber_price_table': "tests/resources/timber_price_table.csv"}

        _, aggrs = cross_cut_felled_trees(payload, **operation_parameters)
        res = aggrs.get_list_result("cross_cutting")
        self.assertEqual(res[0].time_point, 20)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].source, "thinning_from_below")
        self.assertEqual(aggrs.get_list_result('felled_trees')[1].cross_cut_done, True)


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
                    "felled_trees": [CrossCuttableTree(
                                    stems_to_cut_per_ha = 0.006261167484111818,
                                    species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                    breast_height_diameter = 15.57254199723247,
                                    height = 18.293846547993535,
                                    source = "thinning_from_below",
                                    time_point=20,
                                    cross_cut_done=False
                    )]
                },
            ),
        )

        stand, aggrs = cross_cut_felled_trees(payload, **operation_parameters)
        res = aggrs.get_list_result("cross_cutting")
        self.assertEqual(len(res), 2)

        # after the first cross cutting (above), add new thinning results, which need to be cross cut
        aggrs.operation_results["felled_trees"].append(
            CrossCuttableTree(
                stems_to_cut_per_ha = 0.006261167484111818,
                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                breast_height_diameter = 15.57254199723247,
                height = 18.293846547993535,
                source = "thinning_from_below",
                time_point=30,
                cross_cut_done=False
            ),
        )

        payload = (stand, aggrs)

        _, aggrs = cross_cut_felled_trees(payload, **operation_parameters)
        res = aggrs.get_list_result("cross_cutting")
        # test that the results of both cross cut operations are in thinned_trees_cross_cut
        self.assertEqual([r.time_point for r in res], [20, 20, 30, 30])
        self.assertEqual(len(res), 4)


    def test_cross_cut_standing_trees(self):
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

        new_stand, aggrs = cross_cut_standing_trees(payload, **operation_parameters)
        res = aggrs.get_list_result("cross_cutting")
        self.assertEqual(len(res), 6)
        self.assertEqual(res[0].source, "standing_trees")
        
        # test that cross_cut_whole_stand has not modified the trees
        self.assertEqual(
            [rt.stems_per_ha for rt in stand.reference_trees], 
            [rt.stems_per_ha for rt in new_stand.reference_trees]
            )


    def test_cross_cut_standing_trees_called_twice(self):
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

        stand, aggrs = cross_cut_standing_trees(payload, **operation_parameters)
        aggrs.current_time_point=2
        _, aggrs = cross_cut_standing_trees((stand, aggrs), **operation_parameters)
        res = aggrs.get_list_result("cross_cutting")
        self.assertEqual(len(res), 4)
        self.assertEqual([r.time_point for r in res], [1, 1, 2, 2])


    def test_cross_cut_thinning_output(self):
        stand_area = 1.93
        thinned_trees = [
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.006261167484111818,
                                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                breast_height_diameter = 15.57254199723247,
                                height = 18.293846547993535,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.003917869416142222,
                                species = TreeSpecies.PINE,
                                breast_height_diameter = 16.071397406682646,
                                height = 23.617432525999664,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.008092431491823593,
                                species = TreeSpecies.SPRUCE,
                                breast_height_diameter = 17.721245087039236,
                                height = 16.353742669109522,
                                source="thin1",
                                time_point=0
                            )
                        ]

        results = []
        for tree in thinned_trees:
            results.extend(cross_cut_tree(tree, stand_area, DEFAULT_TIMBER_PRICE_TABLE))

        self.assertEqual(len(results), 6)
        self.assertAlmostEqual(sum([r.value_per_ha for r in results]), 0.05577748139, places=6)
        self.assertAlmostEqual(sum([r.volume_per_ha for r in results]), 0.0032810283, places=6)

    def test_cross_cut_returns_three_timber_grades(self):
        stand_area = 1.93
        thinning_output = [
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.006261167484111818,
                                species = TreeSpecies.UNKNOWN_CONIFEROUS,
                                breast_height_diameter = 15.57254199723247,
                                height = 18.293846547993535,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.003917869416142222,
                                species = TreeSpecies.PINE,
                                breast_height_diameter = 16.071397406682646,
                                height = 23.617432525999664,
                                source="thin1",
                                time_point=0
                            ),
                            CrossCuttableTree(
                                stems_to_cut_per_ha = 0.008092431491823593,
                                species = TreeSpecies.SPRUCE,
                                breast_height_diameter = 17.721245087039236,
                                height = 16.353742669109522,
                                source="thin1",
                                time_point=0
                            )
                        ]
        
        results = []
        for tree in thinning_output:
            results.extend(cross_cut_tree(tree, stand_area, TIMBER_PRICE_TABLE_THREE_GRADES))

        grades = [r.timber_grade for r in results]
        unique_grades = set(grades)
        self.assertEqual(len(unique_grades), 3)

class CrossCuttableTreesTest(unittest.TestCase):
    def test_CrossCuttableTrees_from_stand(self):
        stand = ForestStand(
            reference_trees=[
                ReferenceTree(
                    species=TreeSpecies.PINE,
                    breast_height_diameter=45.678,
                    height=28.43,
                    stems_per_ha=22.3
                )
            ],
            area=296.23
        )

        res = cross_cuttable_trees_from_stand(stand, source="thin1", time_point=0)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].species, TreeSpecies.PINE)
        self.assertEqual(res[0].breast_height_diameter, 45.678)
        self.assertEqual(res[0].height, 28.43)
        self.assertAlmostEqual(res[0].stems_to_cut_per_ha, 22.3, places=6)


class CrossCutResultTest(unittest.TestCase):
    fixture = CrossCutResult(
            species=TreeSpecies.PINE,
            timber_grade=1,
            volume_per_ha=2.0,
            value_per_ha=10.0,
            stand_area=2.0,
            source="thin1",
            time_point=0
        )

    def test_get_real_volume(self):
        self.assertEqual(self.fixture.get_real_volume(), 4.0)

    def test_get_real_value(self):
        self.assertEqual(self.fixture.get_real_value(), 20.0)
