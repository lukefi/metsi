import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
import rpy2.robjects as robjects
from forestry import r_utils, cross_cutting
class CrossCuttingTest(unittest.TestCase):

    def test_cross_cut_tree(self):

        robjects.r.source("r/cross_cutting/cross_cutting_main.R")
        
        #parameters: species, dbh, height
        result = robjects.r["cross_cut"]("pine", 30, 25)
        result = r_utils.convert_r_named_list_to_py_dict(result)

        self.assertAlmostEqual(result["volumes"][0], 0.6928, 4)
        self.assertAlmostEqual(result["values"][0], 39.9789, 4)

        # cross cutting is done individually to each referenceTree (use dbh, height and species)
        # pass in Puutavaralajimäärittelyt.txt? <-- this probably needs to be user-inputted?

    def test_cross_cut_stand_returns_total_values(self):
        """This test ensures that the cross_cut_stand returns values that are multiplied by the reference tree's stem count per ha and the stand area."""
       
       #parameter values selected arbitrarily 
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


