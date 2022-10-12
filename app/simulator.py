import time
from typing import List, Callable, Dict
import sys
import forestry.operations
import forestry.preprocessing as preprocessing
from sim.core_types import AggregatedResults, OperationPayload
from sim.runners import run_full_tree_strategy, run_partial_tree_strategy, evaluate_sequence
from sim.generators import simple_processable_chain
from forestdatamodel.model import ForestStand
from app.file_io import read_input_file, simulation_declaration_from_yaml_file, write_result_to_file
from app.app_io import sim_cli_arguments

start_time = time.time_ns()

def runtime_now() -> float:
    global start_time
    return round((time.time_ns() - start_time) / 1000000000, 1)

def print_logline(message: str):
    print("{} {}".format(runtime_now(), message))

def print_stand_result(stand: ForestStand):
    print("volume {}".format(forestry.operations.compute_volume(stand)))


def print_run_result(results: dict):
    for id in results.keys():
        for i, result in enumerate(results[id]):
            print("{} variant {} result: ".format(id, i), end='')
            print_stand_result(result.simulation_state)
            last_volume_reporting_aggregate = result.aggregated_results.prev('report_volume')
            last_biomass_reporting_aggregate = result.aggregated_results.prev('report_biomass')
            last_removal_reporting_aggregate = result.aggregated_results.prev('report_overall_removal')
            print("variant {} growth report: {}".format(i, last_volume_reporting_aggregate))
            print("variant {} biomass report: {}".format(i, last_biomass_reporting_aggregate))
            print("variant {} thinning report: {}".format(i, last_removal_reporting_aggregate))

def preprocess_stands(stands: List[ForestStand], simulation_declaration: dict) -> List[ForestStand]:
    preprocessing_operations = simulation_declaration.get('preprocessing_operations', {})
    preprocessing_params = simulation_declaration.get('preprocessing_params', {})
    preprocessing_funcs = simple_processable_chain(preprocessing_operations, preprocessing_params, preprocessing.operation_lookup)
    stands = evaluate_sequence(stands, *preprocessing_funcs)
    return stands

def run_stands(
        stands: List[ForestStand], simulation_declaration: dict,
        run_strategy: Callable[[OperationPayload, dict, dict], List[OperationPayload]]
) -> Dict[str, List[OperationPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given run strategy. Return the
    results organized into a dict keyed with stand identifiers."""

    retval = {}
    for stand in stands:
        print_logline("Simulating stand {}".format(stand.identifier))
        payload = OperationPayload(
            simulation_state=stand,
            aggregated_results=AggregatedResults(),
            operation_history=[],
        )
        result = run_strategy(payload, simulation_declaration, forestry.operations.operation_lookup)
        retval[stand.identifier] = result
        print_logline("Produced {} variants for stand {}".format(len(result), stand.identifier))
    return retval


def resolve_strategy_runner(source: str) -> Callable:
    strategy_map = {
        'full': run_full_tree_strategy,
        'partial': run_partial_tree_strategy
    }

    try:
        return strategy_map[source]
    except Exception:
        raise Exception("Unable to resolve alternatives tree formation strategy '{}'".format(source))

def main():

    app_arguments = sim_cli_arguments(sys.argv[1:])

    simulation_declaration = simulation_declaration_from_yaml_file(app_arguments.control_file)
    output_filename = app_arguments.output_file

    stands = read_input_file(app_arguments.input_file, app_arguments.input_format)
    print_logline("Preprocessing...")
    result = preprocess_stands(stands, simulation_declaration)

    if app_arguments.strategy != "skip":
        print_logline("Simulating...")
        strategy_runner = resolve_strategy_runner(app_arguments.strategy)
        result = run_stands(result, simulation_declaration, strategy_runner)
        print_run_result(result)

    print_logline("Writing output...")
    write_result_to_file(result, output_filename, app_arguments.output_format)


if __name__ == "__main__":
    main()
