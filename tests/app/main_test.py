"""
This file contains tests for the main functions of the simulator and post processing applications.
The tests write into sys.argv to simulate calling the applications from the command line.
NOTE: the tests use the control.yaml and pp_control.yaml files from the project root to easily test the most recent versions of them.
"""

import os
import sys
import shutil
import unittest
from pathlib import Path
from app import mela2
from typing import List


def run_simulator(state_input_files: List[str], state_output_containers: List[str]):

    strategies = ['full', 'partial']
    control_file = 'tests/resources/main_test/main_test_control.yaml'
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
            output_details.append(f"outdir{i}-{strategy}")

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
            '-r',
            'preprocess,simulate',
            input_file,
            output_dir,
            control_file
        ]
        mela2.main()
    return output_details


class MainTest(unittest.TestCase):

    input_files = [
        'tests/resources/main_test/two_ffc_stands.pickle',
        'tests/resources/main_test/two_vmi12_stands_as_jsonpickle.json'
    ]
    input_containers = [
        'pickle',
        'json'
    ]

    def verify_result_dir(self, outdir):
        _, stands, _ = next(os.walk(outdir))
        self.assertEqual(2, len(stands))
        for stand in stands:
            _, schedules, _ = next(os.walk(Path(outdir, stand)))
            self.assertEqual(8, len(schedules))
            for schedule in schedules:
                _, _, files = next(os.walk(Path(outdir, stand, schedule)))
                self.assertEqual(2, len(files))

    def test_sim_main(self):
        sim_results = run_simulator(self.input_files, self.input_containers)
        for output_dir in sim_results:
            self.verify_result_dir(output_dir)
            preprocessing_filepath = Path(output_dir, 'preprocessing_result.pickle')
            self.assertTrue(os.path.exists(preprocessing_filepath))
            shutil.rmtree(output_dir)

    def test_post_processing_main(self):
        sim_results = run_simulator(self.input_files, self.input_containers)
        for i, sim_dir in enumerate(sim_results):
            pp_input_dir = sim_dir
            pp_control_file = 'tests/resources/main_test/pp_test_control.yaml'
            pp_output_dir = 'pp_outdir'

            sys.argv = [
                'foo',
                pp_input_dir,
                pp_output_dir,
                pp_control_file,
                '-r',
                'postprocess'
            ]

            mela2.main()

            self.verify_result_dir(pp_output_dir)
            shutil.rmtree(pp_output_dir)
            shutil.rmtree(sim_dir)
