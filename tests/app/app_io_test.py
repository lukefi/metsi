import unittest
import pytest
from lukefi.metsi.app.utils import ConfigurationException
from lukefi.metsi.app.app_io import MetsiConfiguration, RunMode, \
    parse_cli_arguments, generate_program_configuration


class TestAppIO(unittest.TestCase):

    def test_sim_cli_arguments(self):
        args = ['input.pickle', 'output2', 'control.yaml', '-f', 'partial', '-e', 'depth', '--state-format',
                'fdm', '--measured-trees', '--strata-origin', '2', '-r', 'preprocess,simulate,export']
        result = parse_cli_arguments(args)
        self.assertEqual(15, len(result.__dict__.keys()))
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
        self.assertEqual("preprocess,simulate,export", result.run_modes)

    def test_control_configurations(self):
        args = ['cli_input', 'cli_output', 'cli_control.yaml', '-s', 'full', '--state-format', 'vmi12', '--state-output-container', 'json']
        cli_args = parse_cli_arguments(args)
        control_args = {'state_output_container': 'pickle', 'preprocessing_output_container': 'json', 'run_modes': 'preprocess,simulate'}
        result = generate_program_configuration(cli_args, control_args)
        self.assertEqual('cli_input', result.input_path)
        self.assertEqual('cli_control.yaml', result.control_file)
        self.assertEqual('cli_output', result.target_directory)
        self.assertEqual('full', result.formation_strategy)
        self.assertEqual('vmi12', result.state_format)
        self.assertEqual('json', result.state_output_container)  # CLI overrides control source
        self.assertEqual('json', result.preprocessing_output_container)  # control source overrides Mela2Configuration
        self.assertEqual(None, result.derived_data_output_container)  # Mela2Configuration default
        self.assertEqual([RunMode.PREPROCESS, RunMode.SIMULATE], result.run_modes)


class TestRunModes(unittest.TestCase):
    def test_valid_typical_run_modes(self):
        modes = ['preprocess', 'export_prepro', 'simulate', 'postprocess', 'export']
        result = MetsiConfiguration._validate_and_sort_run_modes(modes)
        self.assertEqual(result, [RunMode.PREPROCESS, RunMode.EXPORT_PREPRO, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT])


    def test_valid_run_modes_sorted(self):
        modes = ['simulate', 'PREPROCESS', 'export']
        result = MetsiConfiguration._validate_and_sort_run_modes(modes)
        self.assertEqual(result, [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.EXPORT])

    def test_valid_run_modes_with_dependencies(self):
        modes = ['simulate', 'postprocess', 'export']
        result = MetsiConfiguration._validate_and_sort_run_modes(modes)
        self.assertEqual(result, [RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT])

    def test_invalid_run_mode(self):
        modes = ['simulate', 'invalid_mode']
        self.assertRaises(ConfigurationException,
                          MetsiConfiguration._validate_and_sort_run_modes,
                          modes)

    def test_export_prepro_without_preprocess(self):
        modes = ['export_prepro']
        self.assertRaises(ConfigurationException, 
                          MetsiConfiguration._validate_and_sort_run_modes,
                          modes)

    def test_export_without_simulate_or_postprocess(self):
        modes = ['export']
        self.assertRaises(ConfigurationException, 
                          MetsiConfiguration._validate_and_sort_run_modes,
                          modes)


