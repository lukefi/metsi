import time
from typing import List, Callable, Dict
import sys
import forestry.operations
from sim.core_types import OperationPayload
from sim.runners import run_full_tree_strategy, run_partial_tree_strategy
from forestdatamodel.model import ForestStand
from app.file_io import forest_stands_from_json_file, simulation_declaration_from_yaml_file, pickle_writer
from app.app_io import parse_cli_arguments


def print_stand_result(stand: ForestStand):
    print("volume {}".format(forestry.operations.compute_volume(stand)))


def print_run_result(results: dict):
    for id in results.keys():
        print("Results for stand {}; obtained {} variants:".format(id, len(results[id])))
        for i, result in enumerate(results[id]):
            print("variant {} result: ".format(i), end='')
            print_stand_result(result.simulation_state)
            last_reporting_aggregate = list(result.aggregated_results.get('report_volume').values())[-1]
            print("variant {} growth report: {}".format(i, last_reporting_aggregate))


def run_stands(
        stands: List[ForestStand], simulation_declaration: dict,
        run_strategy: Callable[[OperationPayload, dict, dict], List[OperationPayload]]
) -> Dict[str, List[OperationPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given run strategy. Return the
    results organized into a dict keyed with stand identifiers."""

    retval = {}
    for stand in stands:
        payload = OperationPayload(
            simulation_state=stand,
            run_history={},
            aggregated_results={}
        )
        result = run_strategy(payload, simulation_declaration, forestry.operations.operation_lookup)
        retval[stand.identifier] = result
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
    app_arguments = parse_cli_arguments(sys.argv[1:])
    stands = forest_stands_from_json_file(app_arguments.domain_state_file)
    simulation_declaration = simulation_declaration_from_yaml_file(app_arguments.control_file)
    output_filename = app_arguments.output_file
    strategy_runner = resolve_strategy_runner(app_arguments.strategy)

    run_time = int(time.time_ns())
    run_result = run_stands(stands, simulation_declaration, strategy_runner)
    run_time = (int(time.time_ns()) - run_time) / 1000000000
    print_run_result(run_result)
    pickle_writer(output_filename, run_result)
    print("Run in {}".format(run_time))


if __name__ == "__main__":
    main()
