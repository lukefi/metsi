import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
import rpy2.robjects as robjects
from forestry import r_utils, cross_cutting


class CrossCuttingTest(unittest.TestCase):

    def test_cross_cut_tree(self):

        robjects.r.source("r/cross_cutting/cross_cutting_main.R")

        # parameters: species, dbh, height
        result = robjects.r["cross_cut"]("pine", 30, 25)
        result = r_utils.convert_r_named_list_to_py_dict(result)

        self.assertAlmostEqual(result["volumes"][0], 0.6928, 4)
        self.assertAlmostEqual(result["values"][0], 39.9789, 4)

        # cross cutting is done individually to each referenceTree (use dbh, height and species)
        # pass in Puutavaralajimäärittelyt.txt? <-- this probably needs to be user-inputted?

    def test_cross_cut_stand_returns_total_values(self):
        """This test ensures that the cross_cut_stand returns values that are multiplied by the reference tree's stem count per ha and the stand area."""

       # parameter values selected arbitrarily
        tree = ReferenceTree(
            species=TreeSpecies.PINE,
            breast_height_diameter=45.678,
            height=28.43,
            stems_per_ha=22.3
        )

        stand = ForestStand(
            reference_trees=[tree],
            area=296.23
        )

        volumes, values = cross_cutting.cross_cut_stand(stand)

        self.assertEqual(volumes[0], [12.459322454417418, 0.26732088300923035])
        self.assertEqual(values[0], [735.1000248106276, 4.544455011156915])

    def test_cross_cut_thinning_output(self):

        thinned_trees = {
            '001-tree': {
                         'stems_removed_per_ha': 0.006261167484111818,
                         'species': TreeSpecies.UNKNOWN_CONIFEROUS,
                         'breast_height_diameter': 15.57254199723247,
                         'height': 18.293846547993535,
                         'stems_per_ha': 0.2024444153196156,
                         'stand_area': 1.93
                         },
            '002-tree': {
                        'stems_removed_per_ha':0.003917869416142222,
                        'species':TreeSpecies.PINE,
                        'breast_height_diameter':16.071397406682646,
                        'height':23.617432525999664,
                        'stems_per_ha':0.131181075968072,
                        'stand_area':1.93
                        },
            '003-tree': {
                        'stems_removed_per_ha': 0.008092431491823593,
                        'species': TreeSpecies.SPRUCE,
                        'breast_height_diameter':17.721245087039236,
                        'height':16.353742669109522,
                        'stems_per_ha':0.2809229789304476,
                        'stand_area':1.93
                        },
        }

        volumes, values = cross_cutting.cross_cut_thinning_output(thinned_trees)

        self.assertEqual(volumes[0], [0.0, 1.8820884719657113e-06])
        self.assertEqual(volumes[1], [0.0, 1.566128712970515e-06])
        self.assertEqual(volumes[2], [1.4419059383590385e-06, 1.3865035819964635e-06])

        self.assertEqual(values[0], [0.0, 3.199550402341709e-05])
        self.assertEqual(values[1], [0.0, 2.662418812049875e-05])
        self.assertEqual(values[2], [7.930482660974712e-05, 2.357056089393987e-05])



