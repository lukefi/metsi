import sys
from typing import List, Dict

from app.app_io import post_processing_cli_arguments
from app.file_io import simulation_declaration_from_yaml_file, read_simulation_results_input_file, write_post_processing_result_to_file
from forestry.operations import operation_lookup
from sim.core_types import OperationPayload
from sim.generators import simple_processable_chain
from sim.runners import evaluate_sequence


def main():

    app_arguments = post_processing_cli_arguments(sys.argv[1:])
    input_data: Dict[str, List[OperationPayload]] = read_simulation_results_input_file(app_arguments.input_file, app_arguments.input_format)

    control_declaration = simulation_declaration_from_yaml_file(app_arguments.control_file)
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
            result[identifier].append(processed_schedule)

    write_post_processing_result_to_file(result, app_arguments.target_directory, app_arguments.output_format)


if __name__ == '__main__':
    main()
