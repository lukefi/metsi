import argparse
from enum import Enum
from types import SimpleNamespace
from typing import Optional


class RunMode(Enum):
    PREPROCESS = "preprocess"
    SIMULATE = "simulate"
    POSTPROCESS = "postprocess"
    EXPORT = "export"
    EXPORT_PREPRO = "export_prepro"


class MetsiConfiguration(SimpleNamespace):
    input_path = None
    target_directory = None
    control_file = "control.py"
    run_modes = [RunMode.PREPROCESS, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]
    state_format = "fdm"
    state_input_container = "csv"
    state_output_container = None
    derived_data_output_container = None
    formation_strategy = "partial"
    evaluation_strategy = "depth"
    measured_trees = False
    strata = True
    strata_origin = "1"

    def __init__(self, **kwargs):
        if kwargs.get('run_modes') is not None:
            self.set_run_modes(kwargs['run_modes'])
            kwargs.__delitem__('run_modes')
        super().__init__(**kwargs)

    def set_run_modes(self, run_modes: str):
        try:
            if isinstance(run_modes, list):
                self.run_modes = [RunMode(mode) for mode in run_modes]
            else:
                self.run_modes = [RunMode(mode) for mode in run_modes.split(",")]
        except ValueError:
            allowed_modes = ", ".join(mode.value for mode in RunMode)
            raise ValueError(f"Invalid run modes '{run_modes}'. Allowed modes: {allowed_modes}")


def remove_nones(source: dict) -> dict:
    """Return a dict with items from 'source' with keys mapping to None removed"""
    filtered = {}
    for k, v in source.items():
        if v is not None:
            filtered[k] = v
    return filtered


def generate_program_configuration(cli_args: argparse.Namespace, control_source: dict={}) -> MetsiConfiguration:
    """Generate a Mela2Configuration, overriding values with control file source, then with CLI arguments"""
    cli_source = remove_nones(cli_args.__dict__)

    # DEPRECATED: Backwards compatiblity until next version
    if control_source.get('strategy') is not None:
        control_source['formation_strategy'] = control_source.get('strategy')
        control_source.__delitem__('strategy')
    if cli_source.get('strategy') is not None:
        cli_source['formation_strategy'] = cli_source.get('strategy')
        cli_source.__delitem__('strategy')

    merged = {**control_source, **cli_source}
    result = MetsiConfiguration(**merged)
    return result


# NOTE: Q: käytetäänkö tätä edes missään?
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


def parse_cli_arguments(args: list[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 forest growth calculator. CLI arguments override matching control file arguments.')
    parser.add_argument('input_path', help='Application input file or directory')
    parser.add_argument('target_directory', help='Directory path for program output')
    parser.add_argument('control_file', nargs='?', help='Application control declaration file')
    parser.add_argument('-r', '--run-modes',
                        help='Comma separated list of run modes. Possible modes: preprocess,simulate,postprocess,export',
                        type=str)
    parser.add_argument('-s', '--strategy',
                        type=str,
                        help='Simulation event tree formation strategy: \'full\', \'partial\' (default). DEPRECATION WARNING: migrate to using --formation-strategy')
    parser.add_argument('-f', '--formation-strategy',
                        type=str,
                        help='Simulation event tree formation strategy: \'full\', \'partial\' (default)')
    parser.add_argument('-e', '--evaluation-strategy',
                        type=str,
                        help='Simulation event tree evaluation strategy: \'depth\' (default), \'chains\'')
    parser.add_argument('--state-format',
                        choices=['fdm', 'vmi12', 'vmi13', 'xml', 'gpkg'],
                        type=str,
                        help='Data format of the state input file: fdm (default), vmi12, vmi13, xml, gpkg')
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
    parser.add_argument('--measured-trees',
                        action=argparse.BooleanOptionalAction,
                        help="Include measured trees from VMI data source.")
    parser.add_argument('--strata',
                        action=argparse.BooleanOptionalAction,
                        help="Include strata from VMI data source.")
    parser.add_argument('--strata-origin',
                        choices=['1', '2', '3'],
                        type=str,
                        help='Stratum origin type selector for Forest Centre data. Default \'1\'.')
    parser.add_argument('-m', '--multiprocessing', 
                        action=argparse.BooleanOptionalAction,
                        help="Enable parallel simulation of computational units over the amount of CPU cores available. DEPRECATED: ignored")
    return parser.parse_args(args)
