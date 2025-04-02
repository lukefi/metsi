import argparse
from enum import IntEnum
from types import SimpleNamespace
from lukefi.metsi.app.utils import ConfigurationException


class RunMode(IntEnum):
    PREPROCESS = 1
    EXPORT_PREPRO = 2
    SIMULATE = 3
    POSTPROCESS = 4
    EXPORT = 5

    @classmethod
    def from_str(cls, name: str):
        try:
            return cls[name.upper()]
        except KeyError:
            raise ValueError(f"Invalid run mode: {name}")

    def __str__(self):
        return self.name
    
    def __eq__(self, value):
        if isinstance(value, str):
            return self.name.lower() == value.lower()
        return super().__eq__(value)
    
    def __hash__(self):
        return hash(self.name)


class MetsiConfiguration(SimpleNamespace):
    input_path = None
    target_directory = None
    control_file = "control.py"
    run_modes = [RunMode.PREPROCESS, RunMode.EXPORT_PREPRO, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]
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
        run_modes = kwargs.get('run_modes')
        if run_modes is not None:
            run_modes = run_modes.split(',') if isinstance(run_modes, str) else run_modes
            self.run_modes = self._validate_and_sort_run_modes(run_modes)
            kwargs.__delitem__('run_modes')
        super().__init__(**kwargs)

    @staticmethod
    def _validate_and_sort_run_modes(modes: list[str]) -> list[RunMode]:
        try:
            # given input to run mode instances 
            mode_enums = [ RunMode.from_str(p) for p in modes ]
        except ValueError as e:
            raise ConfigurationException(e)  # Return error if invalid run mode

        sorted_modes = sorted(mode_enums)

        # Verify order conditions
        if RunMode.EXPORT_PREPRO in sorted_modes and RunMode.PREPROCESS not in sorted_modes:
            raise ConfigurationException(f"Error: Run mode { RunMode.EXPORT_PREPRO } can not be without { RunMode.POSTPROCESS }")

        if RunMode.EXPORT in sorted_modes and not any(p in sorted_modes for p in [RunMode.SIMULATE, RunMode.POSTPROCESS]):
            raise ConfigurationException(f"Error: Run mode { RunMode.EXPORT } is possible when { RunMode.SIMULATE } or { RunMode.POSTPROCESS } is included")

        return [p for p in sorted_modes]


def _remove_nones(data: dict) -> dict:
    """Internal function to remove None values from a dict."""
    return { k:v for k,v in data.items() if v is not None }


def generate_program_configuration(cli_args: argparse.Namespace, control_source: dict={}) -> MetsiConfiguration:
    """ Factory for generating a MetsiConfiguration. CLI values are overriden with control file source."""
    cli_source = _remove_nones(cli_args.__dict__)

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


def parse_cli_arguments(args: list[str]):
    parser = argparse.ArgumentParser(description='Mela2.0 forest growth calculator. CLI arguments override matching control file arguments.')
    parser.add_argument('input_path', help='Application input file or directory')
    parser.add_argument('target_directory', help='Directory path for program output')
    parser.add_argument('control_file', nargs='?', help='Application control declaration file')
    parser.add_argument('-r', '--run-modes',
                        help='Comma separated list of run modes. Possible modes: preprocess,export_prepro,simulate,postprocess,export',
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

__all__ = [
    'MetsiConfiguration',
    'RunMode',
    'generate_program_configuration',
    'parse_cli_arguments',
]
