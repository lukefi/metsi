import unittest
import sim.util as util

class UtilTest(unittest.TestCase):

    def test_join_two_dicts_no_overwrite(self):
        dict1 = {"one": 1, "two": 2, "three": 3}
        dict2 = {"one": 1, "two": 2, "four":4}
        dict3 = {"five": 5}

        self.assertRaises(Exception, util.join_two_dicts_no_overwrite, [dict1, dict2])
        self.assertEqual(util.join_two_dicts_no_overwrite(dict1, dict3), {"one": 1, "two": 2, "three": 3, "five":5})
