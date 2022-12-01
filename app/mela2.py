import os
import sys

import app.preprocessor
from app.app_io import parse_cli_arguments, Mela2Configuration, generate_program_configuration, RunMode
from app.app_types import SimResults
from forestry.forestry_types import StandList
from app.export import export_variables
from app.file_io import simulation_declaration_from_yaml_file, prepare_target_directory, read_stands_from_file, \
    read_full_simulation_result_dirtree, determine_file_path, write_stands_to_file, write_full_simulation_result_dirtree
from app.post_processing import post_process_alternatives
from app.simulator import simulate_alternatives
from app.console_logging import print_logline


def preprocess(config: Mela2Configuration, control: dict, stands: StandList) -> StandList:
    print_logline("Preprocessing...")
    result = app.preprocessor.preprocess_stands(stands, control)
    if config.preprocessing_output_container is not None:
        print_logline(f"Writing preprocessed data to '{config.target_directory}/preprocessing_result.{config.preprocessing_output_container}'")
        filepath = determine_file_path(config.target_directory, f"preprocessing_result.{config.preprocessing_output_container}")
        write_stands_to_file(result, filepath, config.preprocessing_output_container)
    return result


def simulate(config: Mela2Configuration, control: dict, stands: StandList) -> SimResults:
    print_logline("Simulating alternatives...")
    result = simulate_alternatives(config, control, stands)
    if config.state_output_container is not None or config.derived_data_output_container is not None:
        print_logline(f"Writing simulation results to '{config.target_directory}'")
        write_full_simulation_result_dirtree(result, config)
    return result


def post_process(config: Mela2Configuration, control: dict, data: SimResults) -> SimResults:
    print_logline("Post-processing alternatives...")
    result = post_process_alternatives(config, control['post_processing'], data)
    if config.state_output_container is not None or config.derived_data_output_container is not None:
        print_logline(f"Writing post-processing results to '{config.target_directory}'")
        write_full_simulation_result_dirtree(result, config)
    return result


def export(config: Mela2Configuration, control: dict, data: SimResults) -> None:
    print_logline("Exporting data...")
    export_variables(config, control['export'], data)


mode_runners = {
    RunMode.PREPROCESS: preprocess,
    RunMode.SIMULATE: simulate,
    RunMode.POSTPROCESS: post_process,
    RunMode.EXPORT: export
}


def main() -> int:
    cli_arguments = parse_cli_arguments(sys.argv[1:])
    control_file = Mela2Configuration.control_file if cli_arguments.control_file is None else cli_arguments.control_file
    try:
        control_structure = simulation_declaration_from_yaml_file(control_file)
    except IOError:
        print(f"Application control file path '{control_file}' can not be read. Aborting....")
        return 1
    try:
        app_config = generate_program_configuration(cli_arguments, control_structure['app_configuration'])
        prepare_target_directory(app_config.target_directory)
        print_logline("Reading input...")
        if app_config.run_modes[0] in [RunMode.PREPROCESS, RunMode.SIMULATE]:
            input_data = read_stands_from_file(app_config)
        elif app_config.run_modes[0] in [RunMode.POSTPROCESS, RunMode.SIMULATE]:
            input_data = read_full_simulation_result_dirtree(app_config.input_path)
        else:
            raise Exception("Can not determine input data for unknown run mode")
    except Exception as e:
        print(e)
        print("Aborting run...")
        return 1

    current = input_data
    for mode in app_config.run_modes:
        runner = mode_runners[mode]
        current = runner(app_config, control_structure, current)

    _, dirs, files = next(os.walk(app_config.target_directory))
    if len(dirs) == 0 and len(files) == 0:
        os.rmdir(app_config.target_directory)

    return 0


if __name__ == '__main__':
    code = main()
    sys.exit(code)
