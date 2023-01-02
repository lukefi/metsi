"""
This file contains tests for the main functions of the simulator and post processing applications.
The tests write into sys.argv to simulate calling the applications from the command line.
NOTE: the tests use the control.yaml and pp_control.yaml files from the project root to easily test the most recent versions of them.
"""

import os
import sys
import shutil
import unittest
from lukefi.metsi.app import mela2


class MainTest(unittest.TestCase):
    def test_mela2(self):
        sys.argv = [
            'mela2',
            '--state-format',
            'forest_centre',
            '--preprocessing-output-container',
            'csv',
            '-r',
            'preprocess,simulate,postprocess,export',
            'tests/resources/file_io_test/forest_centre.xml',
            'test_outdir'
        ]
        mela2.main()
        self.assertTrue(os.path.exists('test_outdir/preprocessing_result.csv'))
        self.assertTrue(os.path.exists('test_outdir/data.cda'))
        self.assertTrue(os.path.exists('test_outdir/data.xda'))
        self.assertTrue(os.path.exists('test_outdir/trees.txt'))
        self.assertTrue(os.path.exists('test_outdir/timber_sums.txt'))
        shutil.rmtree('test_outdir')
