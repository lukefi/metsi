import unittest
import sim.util as util

class UtilTest(unittest.TestCase):

    def test_merge_operation_params(self):
        dict1 = {"one": 1, "two": 2, "three": 3}
        dict2 = {"one": 1, "two": 2, "four":4}
        dict3 = {"five": 5}

        self.assertRaises(Exception, util.merge_operation_params, [dict1, dict2])
        self.assertEqual(util.merge_operation_params(dict1, dict3), {"one": 1, "two": 2, "three": 3, "five":5})

    