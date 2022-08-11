"""
This file contains tests for the main functions of the simulator and post processing applications.
The tests write into sys.argv to simulate calling the applications from the command line.
NOTE: the tests use the control.yaml and pp_control.yaml files from the project root to easily test the most recent versions of them.
"""

import os
import sys
import unittest
import app.simulator as simulator
import app.post_processing as pp

class MainTest(unittest.TestCase):
    
    def test_sim_main(self):

        input_files_with_formats = [('tests/resources/two_ffc_stands.pickle', 'pickle'), 
                       ('tests/resources/two_vmi12_stands_as_jsonpickle.json', 'json')]
        strategies = ['full', 'partial']
        output_file = 'tests/sim/temp_output.pickle'
        control_file = 'control.yaml'

        for input_file, input_format in input_files_with_formats:
            for strategy in strategies:

                sys.argv = [
                    'foo',
                    '-s',
                    strategy,
                    '-i',
                    input_format,
                    input_file,
                    control_file,
                    output_file
                ]

                simulator.main()

                self.assertTrue(os.path.exists(output_file))

        os.remove('tests/sim/temp_output.pickle')

    def test_post_processing_main(self):

        input_file = 'tests/resources/post_processing_input_two_vmi12_stands.pickle'
        control_file = 'pp_control.yaml'
        output_file = 'tests/resources/temp_output_pp.pickle'

        sys.argv = [
            'foo',
            input_file,
            control_file,
            output_file
        ]

        pp.main()
        
        self.assertTrue(os.path.exists(output_file))

        os.remove('tests/resources/temp_output_pp.pickle')