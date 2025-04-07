import unittest
from lukefi.metsi.app.utils import ConfigurationException
from lukefi.metsi.app.app_io import MetsiConfiguration, RunMode, \
    FormationStrategy, StateFormat, StateOutputFormat, \
    parse_cli_arguments, generate_application_configuration


class TestAppIO(unittest.TestCase):

    def test_sim_cli_arguments(self):
        args = ['input.dat', 'out', 'control.py']
        result = parse_cli_arguments(args)
        self.assertEqual(3, len(result.keys()))
        self.assertEqual('input.dat', result['input_path'])
        self.assertEqual('out', result['target_directory'])
        self.assertEqual('control.py', result['control_file'])

    def test_control_configurations(self):
        args = ['cli_input', 'cli_output', 'cli_control.py']
        cli_args = parse_cli_arguments(args)
        control_args = {
            'state_output_container': 'pickle',
            'run_modes': ['preprocess',
                          'simulate'],
            'multiprocessing': True }
        app_args = {**cli_args, **control_args}
        result = generate_application_configuration(app_args)
        self.assertEqual(args[0], result.input_path)
        self.assertEqual(args[1], result.target_directory)
        self.assertEqual(args[2], result.control_file)
        self.assertEqual(FormationStrategy.PARTIAL, result.formation_strategy) # MetsiConfiguration default
        self.assertEqual(StateFormat.FDM, result.state_format) # MetsiConfiguration default
        self.assertEqual(None, result.derived_data_output_container)  # MetsiConfiguration default
        self.assertEqual(StateOutputFormat.PICKLE, result.state_output_container)  # Overrides default
        self.assertEqual([RunMode.PREPROCESS, RunMode.SIMULATE], result.run_modes)

    def test_control_config_with_invalid_values(self):
        control_args = {'asd123': 123}
        self.assertRaises(ConfigurationException, generate_application_configuration, control_args)


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


