import argparse
from types import SimpleNamespace
from typing import Optional
from lukefi.metsi.app.utils import ConfigurationException
from lukefi.metsi.app.metsi_enum import (
    IntConfigEnum,
    RunMode,
    StateFormat,
    StateInputFormat,
    StateOutputFormat,
    DerivedDataOutputFormat,
    FormationStrategy,
    EvaluationStrategy,
    StrataOrigin,
    StringConfigEnum,
)


# Main configuration class
class MetsiConfiguration(SimpleNamespace):
    """Main configuration class for the application."""

    # Default configuration values
    control_file = "control.py"
    input_path = ""
    target_directory = ""
    run_modes = [RunMode.PREPROCESS, RunMode.EXPORT_PREPRO, RunMode.SIMULATE, RunMode.POSTPROCESS, RunMode.EXPORT]
    state_format = StateFormat.FDM
    state_input_container = StateInputFormat.CSV
    state_output_container: Optional[StateOutputFormat] = None
    derived_data_output_container: Optional[str] = None
    formation_strategy = FormationStrategy.PARTIAL
    evaluation_strategy = EvaluationStrategy.DEPTH
    measured_trees = False
    strata = True
    strata_origin = StrataOrigin.INVENTORY
    multiprocessing = False

    def __init__(self, **kwargs):
        """Initialize the configuration with defaults and user-provided values."""
        merged_config = {**self._defaults(), **kwargs}
        if 'run_modes' in merged_config:
            merged_config['run_modes'] = self._validate_and_sort_run_modes(merged_config['run_modes'])
        converted_config = self._convert_to_config(**merged_config)
        super().__init__(**converted_config)

    @classmethod
    def _defaults(cls):
        """Return a dictionary of default configurations."""
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('_') and not callable(value)}

    def _convert_to_config(self, **kwargs):
        """Convert input values to their appropriate types or enums."""

        config_types: dict[str, type[str] | type[bool]] = {
            'control_file': str,
            'input_path': str,
            'target_directory': str,
            'measured_trees': bool,
            'strata': bool,
            'multiprocessing': bool
        }
        config_enums: dict[str, type[StringConfigEnum] | type[IntConfigEnum]] = {
            'run_modes': RunMode,
            'state_format': StateFormat,
            'state_input_container': StateInputFormat,
            'state_output_container': StateOutputFormat,
            'derived_data_output_container': DerivedDataOutputFormat,
            'formation_strategy': FormationStrategy,
            'evaluation_strategy': EvaluationStrategy,
            'strata_origin': StrataOrigin,
        }
        for key, value in kwargs.items():
            if key not in config_enums and key not in config_types:
                raise ConfigurationException(f"Invalid app level configuration key '{key}'")
            if value and key in config_enums:
                try:
                    if isinstance(value, list):
                        kwargs[key] = [config_enums[key].from_str(v) if isinstance(v, str) else v for v in value]
                    else:
                        kwargs[key] = config_enums[key](value) if not isinstance(value, config_enums[key]) else value
                except (ValueError, KeyError, TypeError) as e:
                    raise ConfigurationException(f"Invalid value for {key}: {value}. Error: {e}") from e
            elif value and key in config_types:
                kwargs[key] = config_types[key](value) if not isinstance(value, config_types[key]) else value
            else:
                kwargs[key] = None
        return kwargs

    @staticmethod
    def _validate_and_sort_run_modes(modes: list[str | RunMode]) -> list[RunMode]:
        """Validate and sort run modes."""
        try:
            mode_enums = [RunMode.from_str(p) if isinstance(p, str) else RunMode(p) for p in modes]
        except ValueError as e:
            raise ConfigurationException(e) from e

        sorted_modes = sorted(mode_enums)

        # Verify order conditions
        if RunMode.EXPORT_PREPRO in sorted_modes and RunMode.PREPROCESS not in sorted_modes:
            raise ConfigurationException(
                f"Error: Run mode {RunMode.EXPORT_PREPRO} cannot be without {RunMode.PREPROCESS}")

        if RunMode.EXPORT in sorted_modes and not any(p in sorted_modes for p in [RunMode.SIMULATE,
                                                                                  RunMode.POSTPROCESS]):
            raise ConfigurationException(
                f"Error: Run mode {RunMode.EXPORT} is possible only when {RunMode.SIMULATE} or "
                f"{RunMode.POSTPROCESS} is included")

        return sorted_modes


# Utility function to remove None values from a dictionary
def _remove_nones(data: dict) -> dict:
    """Remove None values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None}


# Factory function to generate a MetsiConfiguration
def generate_application_configuration(app_configurations: Optional[dict] = None) -> MetsiConfiguration:
    """Factory for generating a MetsiConfiguration."""
    if app_configurations is None:
        app_configurations = {}
    app_configurations = _remove_nones(app_configurations)
    return MetsiConfiguration(**app_configurations)


# CLI argument parser
def parse_cli_arguments(args: list[str]) -> dict:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description='Mela2.0 forest growth calculator')
    parser.add_argument('input_path', help='Application input file or directory')
    parser.add_argument('target_directory', help='Directory path for program output')
    parser.add_argument('control_file', nargs='?', help='Application control declaration file')
    return parser.parse_args(args).__dict__


# Expose public API
__all__ = [
    'MetsiConfiguration',
    'generate_application_configuration',
    'parse_cli_arguments',
]
