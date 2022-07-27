import os
import unittest
import app.simulator as simulator
import app.post_processing as pp

class MainTest(unittest.TestCase):
    
    def test_sim_main(self):
        """Tests the main function of the simulator with different parameter combinations. 
        NOTE: it uses the control.yaml in the root of the project to easily test the most recent version of it."""

        input_files_with_formats = [('tests/resources/two_ffc_stands.pickle', 'pickle'), 
                       ('tests/resources/two_vmi12_stands_as_jsonpickle.json', 'json')]
        strategies = ['full', 'partial']

        for input_file, format in input_files_with_formats:
            for strategy in strategies:
                args = {
                    'input_file': input_file,
                    'control_file': 'control.yaml',
                    'output_file': 'tests/sim/temp_output.pickle',
                    'strategy': strategy,
                    'input_format': format
                }

                simulator.main(args)

                self.assertTrue(True)

        os.remove('tests/sim/temp_output.pickle')

    def test_post_processing_main(self):
        """Tests the main function of the post processing application. 
        NOTE: it uses the pp_control.yaml in the root of the project to easily test the most recent version of it."""

        args = {
            'input_file': 'tests/resources/post_processing_input_two_vmi12_stands.pickle',
            'control_file': 'pp_control.yaml',
            'output_file': 'tests/resources/temp_output_pp.pickle'
        }

        pp.main(args)
        self.assertTrue(True)

        os.remove('tests/resources/temp_output_pp.pickle')