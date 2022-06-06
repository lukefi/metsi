import argparse
from typing import List


def sim_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 simulator')
    parser.add_argument('domain_state_file', help='A .json file containing the initial state of the simulation')
    parser.add_argument('control_file', help='Simulation control logic as a .yaml file', default='control.yaml')
    parser.add_argument('output_file', help='Simulator output (pickle) file for alternatives and aggregated data')
    parser.add_argument('-s', '--strategy',
                        type=str,
                        help='Simulation alternatives tree formation strategy: \'full\' (default), \'partial\'',
                        default='full')
    return parser.parse_args(args)
