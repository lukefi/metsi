import unittest

import lukefi.metsi.app.app_io
from lukefi.metsi.app import app_io as aio
from lukefi.metsi.app.app_io import set_default_arguments, RunMode


class TestAppIO(unittest.TestCase):
    def test_set_default_io_arguments(self):
        default_io_arguments = {
            'state_format': 'vmi12',
            'state_output_container': 'pickle'
        }
        args = ['input.pickle', 'control.yaml', 'output2', '-s', 'partial', '--state-format', 'fdm', '--measured-trees', '--strata-origin', '2']
        result = set_default_arguments(aio.parse_cli_arguments(args), default_io_arguments)
        self.assertEqual(None, result.preprocessing_output_container)
        self.assertEqual(None, result.state_input_container)
        self.assertEqual('pickle', result.state_output_container)
        self.assertEqual('fdm', result.state_format)

    def test_sim_cli_arguments(self):
        args = ['input.pickle', 'output2', 'control.yaml', '-f', 'partial', '-e', 'depth', '--state-format', 'fdm', '--measured-trees', '--strata-origin', '2']
        result = aio.parse_cli_arguments(args)
        self.assertEqual(16, len(result.__dict__.keys()))
        self.assertEqual('input.pickle', result.input_path)
        self.assertEqual('control.yaml', result.control_file)
        self.assertEqual('output2', result.target_directory)
        self.assertEqual('partial', result.formation_strategy)
        self.assertEqual('depth', result.evaluation_strategy)
        self.assertEqual('fdm', result.state_format)
        self.assertEqual(None, result.state_input_container)
        self.assertEqual(None, result.state_output_container)
        self.assertEqual(True, result.measured_trees)
        self.assertEqual("2", result.strata_origin)

    @unittest.skip
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

        for case in successes:
            result = lukefi.metsi.app.app_io.MetsiConfiguration(run_modes=case[0]).run_modes
            self.assertEqual(case[1], result)
        for case in failures:
            self.assertRaises(Exception, lukefi.metsi.app.app_io.MetsiConfiguration, **{'run_modes': case})

    def test_mela2_configuration(self):
        args = ['cli_input', 'cli_output', 'cli_control.yaml', '-s', 'full', '--state-format', 'vmi12', '--state-output-container', 'json']
        cli_args = aio.parse_cli_arguments(args)
        control_args = {'state_output_container': 'pickle', 'preprocessing_output_container': 'json', 'run_modes': 'preprocess'}
        result = lukefi.metsi.app.app_io.generate_program_configuration(cli_args, control_args)
        self.assertEqual('cli_input', result.input_path)
        self.assertEqual('cli_control.yaml', result.control_file)
        self.assertEqual('cli_output', result.target_directory)
        self.assertEqual('full', result.formation_strategy)
        self.assertEqual('vmi12', result.state_format)
        self.assertEqual('json', result.state_output_container)  # CLI overrides control source
        self.assertEqual('json', result.preprocessing_output_container)  # control source overrides Mela2Configuration
        self.assertEqual(None, result.derived_data_output_container)  # Mela2Configuration default
        self.assertEqual([RunMode.PREPROCESS], result.run_modes)

