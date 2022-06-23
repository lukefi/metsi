import unittest
from forestdatamodel.model import ForestStand, ReferenceTree
import rpy2.robjects as robjects
from forestry import r_utils
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

        
