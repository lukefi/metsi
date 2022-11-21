import sys
from typing import List

import app.file_io
from app.app_io import Mela2Configuration, generate_program_configuration, parse_cli_arguments
from app.file_io import simulation_declaration_from_yaml_file, read_full_simulation_result_dirtree, \
    write_full_simulation_result_dirtree
from forestry.operations import operation_lookup
from sim.core_types import OperationPayload
from sim.generators import simple_processable_chain
from sim.runners import evaluate_sequence


def postprocessing(config: Mela2Configuration, control: dict, input_data: dict[str, list[OperationPayload]]):

    chain = simple_processable_chain(
        control.get('post_processing', []),
        control.get('operation_params', {}),
        operation_lookup
    )
    result = {}
    for identifier, schedules in input_data.items():
        result[identifier] = []
        for schedule in schedules:
            payload = (schedule.simulation_state, schedule.aggregated_results)
            processed_schedule = evaluate_sequence(payload, *chain)
            result[identifier].append(
                OperationPayload(
                    simulation_state=processed_schedule[0],
                    aggregated_results=processed_schedule[1]))
    return result


def main():
    cli_arguments = parse_cli_arguments(sys.argv[1:])
    control_file = Mela2Configuration.control_file if cli_arguments.control_file is None else cli_arguments.control_file
    try:
        control_structure = simulation_declaration_from_yaml_file(control_file)
    except:
        print(f"Application control file path '{control_file}' can not be read. Aborting....")
        return
    app_config = generate_program_configuration(cli_arguments, control_structure['app_configuration'])

    app.file_io.prepare_target_directory(app_config.target_directory)
    input_data: dict[str, List[OperationPayload]] = read_full_simulation_result_dirtree(app_config.input_path)
    control_declaration = simulation_declaration_from_yaml_file(app_config.control_file)
    result = postprocessing(app_config, control_declaration, input_data)
    write_full_simulation_result_dirtree(result, app_config)


if __name__ == '__main__':
    main()
