import unittest

unrunnable = False
try:
    from rpy2 import robjects
except ImportError:
    unrunnable = True


@unittest.skipIf(unrunnable, "rpy2 not installed")
class RTest(unittest.TestCase):
    def test_init(self):
        print(robjects.__version__)

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

    def test_python_to_r_transformations(self):
        vector = [1, 2, 3]
        matrix = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        object = {
            'one': 1,
            'two': [1, 2, 3]
        }

        v = robjects.IntVector(vector)
        m = robjects.r.matrix(robjects.IntVector(matrix), nrow=3)
        df = robjects.DataFrame(object)

        self.assertEqual(vector, list(v))
        self.assertEqual(matrix, list(m))
        self.assertEqual(1, m[0])
        self.assertEqual(['one', 'two.1L', 'two.2L', 'two.3L'], list(df.colnames))

        one = df.rx('one')[0]
        two1 = df.rx('two.1L')[0]
        two2 = df.rx('two.2L')[0]
        two3 = df.rx('two.3L')[0]
        self.assertEqual([1], list(one))
        self.assertEqual([1], list(two1))
        self.assertEqual([2], list(two2))
        self.assertEqual([3], list(two3))



