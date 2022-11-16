import unittest

import app.app_io
from app import app_io as aio
from app.app_io import set_default_arguments, RunMode


class TestAppIO(unittest.TestCase):
    def test_set_default_io_arguments(self):
        default_io_arguments = {
            'state_format': 'vmi12',
            'state_output_container': 'pickle'
        }
        args = ['input.pickle', 'control.yaml', 'output2', '-s', 'partial', '--state-format', 'fdm', '--reference-trees', '--strata-origin', '2']
        result = set_default_arguments(aio.sim_cli_arguments(args), default_io_arguments)
        self.assertEqual(None, result.preprocessing_output_container)
        self.assertEqual(None, result.state_input_container)
        self.assertEqual('pickle', result.state_output_container)
        self.assertEqual('fdm', result.state_format)

    def test_sim_cli_arguments(self):
        args = ['input.pickle', 'control.yaml', 'output2', '-s', 'partial', '--state-format', 'fdm', '--reference-trees', '--strata-origin', '2']
        result = aio.sim_cli_arguments(args)
        self.assertEqual(12, len(result.__dict__.keys()))
        self.assertEqual('input.pickle', result.input_file)
        self.assertEqual('control.yaml', result.control_file)
        self.assertEqual('output2', result.target_directory)
        self.assertEqual('partial', result.strategy)
        self.assertEqual('fdm', result.state_format)
        self.assertEqual(None, result.state_input_container)
        self.assertEqual(None, result.state_output_container)
        self.assertEqual(True, result.reference_trees)
        self.assertEqual("2", result.strata_origin)

    def test_run_modes(self):
        successes = [
            ("preprocess,simulate,postprocess,export", [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]),
            ("preprocess,simulate,export", [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.EXPORT]),
            ("preprocess,simulate,postprocess", [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.POSTPROCESS]),
            ("preprocess,simulate", [RunMode.PREPROCESS, RunMode.SIMULATE]),
            ("preprocess", [RunMode.PREPROCESS]),
            ("simulate,postprocess,export", [RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]),
            ("simulate,postprocess", [RunMode.SIMULATE, RunMode.POSTPROCESS]),
            ("simulate,export", [RunMode.SIMULATE, RunMode.EXPORT]),
            ("simulate", [RunMode.SIMULATE]),
            ("postprocess,export", [RunMode.POSTPROCESS, RunMode.EXPORT]),
            ("postprocess", [RunMode.POSTPROCESS]),
            ("export", [RunMode.EXPORT])
        ]
        failures = [
            "preprocess,postprocess,export",
            "preprocess,postprocess",
            "preprocess,export",
            "simulate,preprocess",
            "postprocess,preprocess",
            "postprocess,simulate",
            "export,preprocess",
            "abc",
            123,
            "preporcess,simulate"
        ]
        fn = app.app_io.Mela2Configuration.parse_run_modes
        for case in successes:
            self.assertEqual(case[1], fn(case[0]))
        for case in failures:
            self.assertRaises(Exception, fn, case)

    def test_post_rocessing_cli_arguments(self):
        args = ['simdir', 'control.yaml', 'outdir']
        result = aio.post_processing_cli_arguments(args)
        self.assertEqual(5, len(result.__dict__.keys()))
        self.assertEqual('simdir', result.input_directory)
        self.assertEqual('control.yaml', result.control_file)
        self.assertEqual('outdir', result.target_directory)

    def test_export_cli_arguments(self):
        args = ['simdir', 'control.yaml']
        result = aio.export_cli_arguments(args)
        self.assertEqual(2, len(result.__dict__.keys()))
        self.assertEqual('simdir', result.input_directory)
        self.assertEqual('control.yaml', result.control_file)
