import unittest
from app import app_io as aio


class TestAppIO(unittest.TestCase):
    def test_sim_cli_arguments(self):
        args = ['input.pickle', 'control.yaml', 'output.pickle', '-s', 'partial', '-i', 'pickle', '--reference-trees', '--strata-origin', '2']
        result = aio.sim_cli_arguments(args)
        self.assertEqual(8, len(result.__dict__.keys()))
        self.assertEqual('input.pickle', result.input_file)
        self.assertEqual('control.yaml', result.control_file)
        self.assertEqual('output.pickle', result.output_file)
        self.assertEqual('partial', result.strategy)
        self.assertEqual(True, result.reference_trees)
        self.assertEqual("2", result.strata_origin)

    def test_post_rocessing_cli_arguments(self):
        args = ['input.json', 'control.yaml', 'output.pickle']
        result = aio.post_processing_cli_arguments(args)
        self.assertEqual(5, len(result.__dict__.keys()))
        self.assertEqual('input.json', result.input_file)
        self.assertEqual('control.yaml', result.control_file)
        self.assertEqual('output.pickle', result.output_file)

    def test_export_cli_arguments(self):
        args = ['input.pickle', 'control.yaml']
        result = aio.export_cli_arguments(args)
        self.assertEqual(2, len(result.__dict__.keys()))
        self.assertEqual('input.pickle', result.input_file)
        self.assertEqual('control.yaml', result.control_file)
