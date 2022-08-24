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
from typing import List


SIM_OUTS = []


def run_simulator(input_files: List[str], input_formats: List[str]):

    strategies = ['full', 'partial']
    control_file = 'control.yaml'
    output_files = []
    for i in input_files:
        file_split = i.split('.')
        output_files.append(file_split[0]+'.sim.out.'+file_split[-1])
    abs_paths = []
    for i in input_files:
        abs_paths.append(os.path.join(os.getcwd(), 'tests', 'resources', i))

    for input_file, input_format, output_file in zip(abs_paths, input_formats, output_files):
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
    return output_files


class MainTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        input_files = [
            'two_ffc_stands.pickle',
            'two_vmi12_stands_as_jsonpickle.json'
        ]
        input_formats = [
            'pickle',
            'json'
        ]
        global SIM_OUTS
        SIM_OUTS = run_simulator(input_files, input_formats)

    def test_sim_main(self):
        for output_file in SIM_OUTS:
            self.assertTrue(os.path.exists(output_file))
            os.remove(output_file)

    def test_post_processing_main(self):
        for output_file in SIM_OUTS:
            pp_input_file = output_file
            pp_control_file = 'pp_control.yaml'
            pp_output_file = 'tests/resources/temp_output_pp.pickle'

            sys.argv = [
                'foo',
                pp_input_file,
                pp_control_file,
                pp_output_file
            ]

            pp.main()

            self.assertTrue(os.path.exists(output_file))

            os.remove('tests/resources/temp_output_pp.pickle')
