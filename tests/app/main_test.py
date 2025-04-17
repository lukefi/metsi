"""
This file contains tests for the main functions of the simulator and post processing applications.
The tests write into sys.argv to simulate calling the applications from the command line.
"""

import os
import sys
import shutil
import unittest
from lukefi.metsi.app import metsi

@unittest.skip
class MainTest(unittest.TestCase):
    def test_metsi(self):
        sys.argv = [
            'metsi',
            '--state-format',
            'xml',
            '--preprocessing-output-container',
            'csv',
            '-r',
            'preprocess,simulate,postprocess,export',
            'tests/resources/file_io_test/forest_centre.xml',
            'test_outdir'
        ]
        metsi.main()
        self.assertTrue(os.path.exists('test_outdir/preprocessing_result.csv'))
        self.assertTrue(os.path.exists('test_outdir/data.cda'))
        self.assertTrue(os.path.exists('test_outdir/data.xda'))
        self.assertTrue(os.path.exists('test_outdir/trees.txt'))
        self.assertTrue(os.path.exists('test_outdir/timber_sums.txt'))
        shutil.rmtree('test_outdir')
