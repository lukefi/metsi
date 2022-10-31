"""
This file contains tests for the main functions of the simulator and post processing applications.
The tests write into sys.argv to simulate calling the applications from the command line.
NOTE: the tests use the control.yaml and pp_control.yaml files from the project root to easily test the most recent versions of them.
"""

import os
import sys
import unittest
from pathlib import Path
import app.simulator as simulator
import app.post_processing as pp
from typing import List


def run_simulator(state_input_files: List[str], state_output_containers: List[str]):

    strategies = ['full', 'partial']
    control_file = 'control.yaml'
    run_details = []
    output_details = []

    for i, (container, file) in enumerate(zip(state_output_containers, state_input_files)):
        for strategy in strategies:
            run_details.append((
                os.path.join(os.getcwd(), file),
                container,
                f"outdir{i}-{strategy}",
                f"output.{container}",
                strategy
            ))
            output_details.append((
                f"outdir{i}-{strategy}",
                f"output.{container}",
                container
            ))

    for input_file, state_output_container, output_dir, _, strategy in run_details:
        sys.argv = [
            'foo',
            '-s',
            strategy,
            '--state-format',
            'fdm',
            '--state-input-container',
            state_output_container,
            '--preprocessing-output-container',
            'pickle',
            '--state-output-container',
            state_output_container,
            input_file,
            control_file,
            output_dir
        ]
        print(sys.argv)
        simulator.main()
    return output_details


class MainTest(unittest.TestCase):

    input_files = [
        'tests/resources/two_ffc_stands.pickle',
        'tests/resources/two_vmi12_stands_as_jsonpickle.json'
    ]
    input_containers = [
        'pickle',
        'json'
    ]

    def test_sim_main(self):
        sim_results = run_simulator(self.input_files, self.input_containers)
        for output_dir, output_file, _ in sim_results:
            filepath = Path(output_dir, output_file)
            preprocessing_filepath = Path(output_dir, 'preprocessing_result.pickle')
            self.assertTrue(os.path.exists(filepath))
            self.assertTrue(os.path.exists(preprocessing_filepath))
            os.remove(filepath)
            os.remove(preprocessing_filepath)
            os.rmdir(output_dir)

    def test_post_processing_main(self):
        sim_results = run_simulator(self.input_files, self.input_containers)
        for i, (sim_dir, sim_file, container) in enumerate(sim_results):
            pp_input_file = os.path.join(os.getcwd(), sim_dir, sim_file)
            pp_control_file = 'pp_control.yaml'
            pp_result_file = 'pp_result.pickle'

            sys.argv = [
                'foo',
                '--input-format',
                container,
                pp_input_file,
                pp_control_file,
                sim_dir
            ]

            pp.main()

            pp_result_path = Path(sim_dir, pp_result_file)
            preprocessing_result_path = Path(sim_dir, 'preprocessing_result.pickle')
            self.assertTrue(os.path.exists(pp_result_path))
            os.remove(pp_result_path)
            os.remove(pp_input_file)
            os.remove(preprocessing_result_path)
            os.rmdir(sim_dir)
