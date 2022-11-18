import sys
from typing import List

import app.file_io
from app.app_io import post_processing_cli_arguments, set_default_arguments
from app.file_io import simulation_declaration_from_yaml_file, read_full_simulation_result_dirtree, \
    write_full_simulation_result_dirtree
from forestry.operations import operation_lookup
from sim.core_types import OperationPayload
from sim.generators import simple_processable_chain
from sim.runners import evaluate_sequence


def main():

    app_arguments = post_processing_cli_arguments(sys.argv[1:])
    app.file_io.prepare_target_directory(app_arguments.target_directory)
    input_data: dict[str, List[OperationPayload]] = read_full_simulation_result_dirtree(app_arguments.input_directory)

    control_declaration = simulation_declaration_from_yaml_file(app_arguments.control_file)
    app_arguments = set_default_arguments(app_arguments, control_declaration['io_configuration'])
    chain = simple_processable_chain(
        control_declaration.get('post_processing', []),
        control_declaration.get('operation_params', {}),
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
    write_full_simulation_result_dirtree(result, app_arguments)


if __name__ == '__main__':
    main()
