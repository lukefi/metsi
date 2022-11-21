import argparse
from enum import Enum
from types import SimpleNamespace
from typing import List, Optional


class RunMode(Enum):
    PREPROCESS = "preprocess"
    SIMULATE = "simulate"
    POSTPROCESS = "postprocess"
    EXPORT = "export"


class Mela2Configuration(SimpleNamespace):
    input_path = None
    target_directory = None
    control_file = "control.yaml"
    run_modes = [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]
    state_format = "fdm"
    state_input_container = "csv"
    state_output_container = "csv"
    preprocessing_output_container = "csv"
    derived_data_output_container = "json"
    strategy = "partial"
    multiprocessing = False
    reference_trees = False  # ForestBuilder parameter
    strata_origin = "1"  # ForestBuilder parameter

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


def merge_dicts(sources: list[dict]=[]) -> dict:
    """Merge dicts in given list of dicts, overriding keys in order."""
    result = {}
    for source in sources:
        result |= source
    return result


def remove_nones(source: dict) -> dict:
    """Return a dict with items from 'source' with keys mapping to None removed"""
    filtered = {}
    for k, v in source.items():
        if v is not None:
            filtered[k] = v
    return filtered


def generate_program_configuration(cli_args: argparse.Namespace, control_source: dict={}) -> Mela2Configuration:
    """Generate a Mela2Configuration, overriding values with control file source, then with CLI arguments"""
    cli_source = remove_nones(cli_args.__dict__)
    merged = merge_dicts([control_source, cli_source])
    return Mela2Configuration(**merged)


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


def parse_cli_arguments(args: List[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 forest growth calculator. CLI arguments override matching control file arguments.')
    parser.add_argument('input_path', help='Application input file or directory')
    parser.add_argument('target_directory', help='Directory path for program output')
    parser.add_argument('control_file', nargs='?', help='Application control declaration file')
    parser.add_argument('-s', '--strategy',
                        type=str,
                        help='Simulation event tree formation strategy: \'full\' (default), \'partial\', \'skip\'')
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
                        action=argparse.BooleanOptionalAction,
                        help="Include reference trees from VMI data source.")
    parser.add_argument('--strata-origin',
                        choices=['1', '2', '3'],
                        type=str,
                        help='Stratum origin type selector for Forest Centre data. Default \'1\'.')
    parser.add_argument('-m', '--multiprocessing', 
                        action=argparse.BooleanOptionalAction,
                        help="Enable parallel simulation of computational units over the amount of CPU cores available.")

    return parser.parse_args(args)
