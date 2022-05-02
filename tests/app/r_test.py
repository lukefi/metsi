import unittest
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.robjects.packages as rpackages


class RTest(unittest.TestCase):
    def test_init(self):
        print(rpy2.__version__)

    def test_sum(self):
        rsum = robjects.r['sum']
        rsort = robjects.r['sort']
        data = [1, 2, 3]
        sum = rsum(robjects.IntVector(data))[0]
        sorted = rsort(robjects.IntVector(data), decreasing=True)
        self.assertEqual(6, sum)
        self.assertEqual(3, sorted[0])

    def test_script_file(self):
        data = 10
        robjects.r.source('tests/resources/double.R')
        result = robjects.r['dbl'](data)
        self.assertEqual(20, result[0])
        self.assertEqual(30, robjects.r['test_var'][0])

    def test_inline_script(self):
        data = 10
        robjects.r('''
        dbl <- function(x) {
            2 * x
        }
        ''')
        result = robjects.r['dbl'](data)
        self.assertEqual(20, result[0])



