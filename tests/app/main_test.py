"""
This file contains tests for the main functions of the simulator and post processing applications.
The tests write into sys.argv to simulate calling the applications from the command line.
"""

import os
import sys
import shutil
import unittest
from lukefi.metsi.app import metsi
import tempfile
from pathlib import Path
from types import SimpleNamespace

@unittest.skip("Not working")
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

class RemoveExistingExportFilesTest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for fake target files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_path = Path(self.temp_dir.name)

        # Create files that match export + preprocessing config
        (self.target_path / "data.xda").write_text("dummy xda")
        (self.target_path / "data.cda").write_text("dummy cda")
        (self.target_path / "custom_export.txt").write_text("dummy export")
        (self.target_path / "preprocessing_result.csv").write_text("dummy csv")

        # Create unrelated file that should NOT be deleted
        (self.target_path / "keep_me.txt").write_text("don't delete me")

        # Mock config object with just the target_directory
        self.config = SimpleNamespace(target_directory=str(self.target_path))

        # Define a control structure that matches the created files
        self.control = {
            "export": [
                {"format": "J", "xda_filename": "data.xda", "cda_filename": "data.cda"},
                {"format": "TXT", "filename": "custom_export.txt"}
            ],
            "export_prepro": {
                "csv": {}
            }
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_remove_existing_export_files(self):
        # Run the function
        metsi.remove_existing_export_files(self.config, self.control)

        # Check that only the export-related files were deleted
        remaining_files = set(f.name for f in self.target_path.iterdir())

        self.assertIn("keep_me.txt", remaining_files)
        self.assertNotIn("data.xda", remaining_files)
        self.assertNotIn("data.cda", remaining_files)
        self.assertNotIn("custom_export.txt", remaining_files)
        self.assertNotIn("preprocessing_result.csv", remaining_files)
