import argparse
from enum import Enum
from types import SimpleNamespace
from typing import List


class RunMode(Enum):
    PREPROCESS = "preprocess"
    SIMULATE = "simulate"
    POSTPROCESS = "postprocess"
    EXPORT = "export"


class Mela2Configuration(SimpleNamespace):
    run_modes = [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]

    def set_run_modes(self, modestring: str):
        self.run_modes = Mela2Configuration.parse_run_modes(modestring)

    @classmethod
    def parse_run_modes(cls, modestring):
        try:
            mode_candidates = list(map(lambda x: RunMode(x), modestring.split(sep=",")))
        except:
            raise Exception(f"Unable to parse run mode list '{modestring}'. "
                            f"Allowed modes: {','.join(map(lambda x: x.value, RunMode))}")
        last = len(mode_candidates) - 1
        for i, candidate in enumerate(mode_candidates):
            if candidate == RunMode.PREPROCESS:
                if i < last and mode_candidates[i + 1] != RunMode.SIMULATE:
                    raise Exception("Run mode 'preprocess' must be followed by 'simulate'")
                if i != 0:
                    raise Exception("Run mode 'preprocess' must be the first mode")
            if candidate == RunMode.SIMULATE:
                if i > 1:
                    raise Exception("Run mode 'simulate' must be up to the second mode")
                if i == 1 and mode_candidates[i - 1] != RunMode.PREPROCESS:
                    raise Exception("Run mode 'simulate' must be preceded by 'preprocess'")
            if candidate == RunMode.POSTPROCESS:
                if i < last - 1:
                    raise Exception("Run mode 'postprocess' must be second from last or last mode")
                if i > 0 and mode_candidates[i - 1] != RunMode.SIMULATE:
                    raise Exception("Run mode 'postprocess' can be preceded only by 'simulate'")
            if candidate == RunMode.EXPORT:
                if i < last:
                    raise Exception("Run mode 'export' must be the last mode")
                if i > 0 and mode_candidates[i - 1] not in (RunMode.SIMULATE, RunMode.POSTPROCESS):
                    raise Exception("Run mode 'export' must be preceded by 'simulate' or 'postprocess'")
        return mode_candidates


def set_default_arguments(cli_args: argparse.Namespace, default_args: dict) -> argparse.Namespace:
    """If args Namespace has its given member as None, in-place replace it with value from defaults"""
    for member in [
        'state_format',
        'state_input_container',
        'state_output_container',
        'preprocessing_output_container',
        'derived_data_output_container'
    ]:
        if cli_args.__dict__.get(member) is None:
            cli_args.__dict__[member] = default_args.get(member)
    return cli_args


def sim_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 simulator')
    parser.add_argument('input_file', help='Simulator input file')
    parser.add_argument('control_file', help='Simulation control declaration file', default='control.yaml')
    parser.add_argument('target_directory', help='Directory path for program output', default='output')
    parser.add_argument('-s', '--strategy',
                        type=str,
                        help='Simulation alternatives tree formation strategy: \'full\' (default), \'partial\', \'skip\'',
                        default='full')
    parser.add_argument('--state-format',
                        choices=['fdm', 'vmi12', 'vmi13', 'forest_centre'],
                        type=str,
                        help='Data format of the state input file: fdm (default), vmi12, vmi13, forest_centre')
    parser.add_argument('--state-input-container',
                        choices=['pickle', 'json', 'csv'],
                        type=str,
                        help='Container format of the state input file: \'pickle\' (default), \'json\', \'csv\'')
    parser.add_argument('--state-output-container',
                        choices=['pickle', 'json', 'csv'],
                        type=str,
                        help='Container format of state output files: \'pickle\' (default), \'json\', \'csv\'')
    parser.add_argument('--preprocessing-output-container',
                        choices=['pickle', 'json', 'csv'],
                        type=str,
                        help='Container format of preprocessing result file: \'pickle\' (default), \'json\', \'csv\'')
    parser.add_argument('--derived-data-output-container',
                        choices=['pickle', 'json'],
                        type=str,
                        help='Container format of derived data result file: \'pickle\' (default), \'json\'')
    parser.add_argument('--reference-trees',
                        default=False,
                        action=argparse.BooleanOptionalAction,
                        help="Include reference trees from VMI data source.")
    parser.add_argument('--strata-origin',
                        default='1',
                        choices=['1', '2', '3'],
                        type=str,
                        help='Stratum origin type selector for Forest Centre data. Default \'1\'.')

    parser.add_argument('-m', '--multiprocessing', 
                        action=argparse.BooleanOptionalAction,
                        help="Enable parallel simulation of computational units over the amount of CPU cores available.",
                        default=False)

    return parser.parse_args(args)


def post_processing_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 post processing')
    parser.add_argument('input_directory', help='Post processing input file (simulator output)')
    parser.add_argument('control_file', help='Post processing control declaration file', default='pp_control.yaml')
    parser.add_argument('target_directory', help='Directory path for program output')
    parser.add_argument('--state-output-container',
                        choices=['pickle', 'json', 'csv'],
                        type=str,
                        help='Container format of state output files: \'pickle\' (default), \'json\', \'csv\'')
    parser.add_argument('--derived-data-output-container',
                        choices=['pickle', 'json'],
                        type=str,
                        help='Container format of derived data result file: \'pickle\' (default), \'json\'')
    return parser.parse_args(args)


def export_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 data export')
    parser.add_argument('input_directory', help='Input directory (simulator or post processing output)')
    parser.add_argument('control_file', help='Export control declaration file', default='export_control.yaml')
    return parser.parse_args(args)
