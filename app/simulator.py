import os
import time
import queue
from typing import List, Callable, Dict
import sys
import multiprocessing
import forestry.operations
import forestry.preprocessing as preprocessing
from sim.runners import run_full_tree_strategy, run_partial_tree_strategy, evaluate_sequence
from sim.core_types import AggregatedResults, OperationPayload
from sim.generators import simple_processable_chain
from forestdatamodel.model import ForestStand
from app.file_io import read_stands_from_file, simulation_declaration_from_yaml_file, \
    write_full_simulation_result_dirtree, prepare_target_directory, \
    determine_file_path, write_stands_to_file
from app.app_io import parse_cli_arguments, Mela2Configuration, generate_program_configuration

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


def run_strategy_multiprocessing_wrapper(payload: OperationPayload, simulation_declaration: dict, operation_lookup: dict, run_strategy: Callable,  queue: queue.Queue) -> None:
    """Wrapper function for running a simulation strategy in a multiprocessing context. The result is placed in the given queue"""
    result = run_strategy(payload, simulation_declaration, operation_lookup)
    queue.put(result)


def run_stands(
        stands: List[ForestStand], simulation_declaration: dict,
        run_strategy: Callable[[OperationPayload, dict, dict], List[OperationPayload]],
        using_multiprocessing: bool
) -> Dict[str, List[OperationPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given run strategy. Return the
    results organized into a dict keyed with stand identifiers."""

    retval = {}
    args = [
     (
        OperationPayload(
            simulation_state=stand,
            aggregated_results=AggregatedResults(),
            operation_history=[],
        ),
        simulation_declaration,
        forestry.operations.operation_lookup
     )
        for stand in stands
    ]

    # Each stand can be simulated independently from each other, therefore they can be run in parallel in separate processes.
    # pool.starmap() will allocate simulation work to available processes. 
    if using_multiprocessing:
        #manager is used to create a shared Queue into which each process can put their result.
        manager = multiprocessing.Manager()
        queue = manager.Queue()

        mp_args = []
        for arg in args:
            mp_args.append(arg + (run_strategy, queue,))

        processes = os.cpu_count()
        with multiprocessing.Pool(processes=processes) as pool:
            pool.starmap(run_strategy_multiprocessing_wrapper, mp_args)

        #collect results from the queue into which the simulation results are put into.
        while not queue.empty():
            result = queue.get()
            retval[result[0].simulation_state.identifier] = result
        
        return retval

    else:
        for arg in args:
            result = run_strategy(*arg)
            id = arg[0].simulation_state.identifier
            print_logline(f"Alternatives for stand {id}: {len(result)}")
            retval[id] = result
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
    cli_arguments = parse_cli_arguments(sys.argv[1:])
    control_file = Mela2Configuration.control_file if cli_arguments.control_file is None else cli_arguments.control_file
    try:
        control_structure = simulation_declaration_from_yaml_file(control_file)
    except:
        print(f"Application control file path '{control_file}' can not be read. Aborting....")
        return
    app_arguments = generate_program_configuration(cli_arguments, control_structure['app_configuration'])

    print_logline("Preparing run...")
    stands = read_stands_from_file(app_arguments)
    outdir = prepare_target_directory(app_arguments.target_directory)

    print_logline("Preprocessing computational units...")
    result = preprocess_stands(stands, control_structure)

    if app_arguments.preprocessing_output_container is not None:
        filepath = determine_file_path(outdir, f"preprocessing_result.{app_arguments.preprocessing_output_container}")
        write_stands_to_file(result, filepath, app_arguments.preprocessing_output_container)

    if app_arguments.strategy != "skip":
        print_logline("Simulating alternatives...")
        strategy_runner = resolve_strategy_runner(app_arguments.strategy)
        result = run_stands(result, control_structure, strategy_runner, app_arguments.multiprocessing)
    else:
        result = {}

    print_logline("Writing output...")
    write_full_simulation_result_dirtree(result, app_arguments)

    print_logline("Done. Exiting.")

if __name__ == "__main__":
    main()
