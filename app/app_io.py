import argparse
from typing import List


def sim_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 simulator')
    parser.add_argument('input_file', help='Simulator input file')
    parser.add_argument('control_file', help='Simulation control declaration file', default='sim_control.yaml')
    parser.add_argument('output_file', help='Simulator output file for alternatives and aggregated data')
    parser.add_argument('-s', '--strategy',
                        type=str,
                        help='Simulation alternatives tree formation strategy: \'full\' (default), \'partial\'',
                        default='full')
    return parser.parse_args(args)


def post_processing_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 post processing')
    parser.add_argument('input_file', help='Post processing input file (simulator output)')
    parser.add_argument('control_file', help='Post processing control declaration file', default='pp_control.yaml')
    parser.add_argument('output_file', help='Post processing output file')
    return parser.parse_args(args)