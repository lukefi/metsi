import time
from typing import List, Callable, Dict
import sys
import forestry.operations
from sim.core_types import OperationPayload
from sim.runners import run_full_tree_strategy, run_partial_tree_strategy
from sim.preprocessing import preprocess_stands
from forestdatamodel.model import ForestStand
from app.file_io import forest_stands_from_json_file, simulation_declaration_from_yaml_file
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


def main():
    app_arguments = parse_cli_arguments(sys.argv[1:])
    simulation_declaration = simulation_declaration_from_yaml_file(app_arguments.control_file)
    stands = forest_stands_from_json_file(app_arguments.domain_state_file)
    stands = preprocess_stands(stands, simulation_declaration['pre_processing'])


    # run full tree
    full_run_time = int(time.time_ns())
    full_run_result = run_stands(stands, simulation_declaration, run_full_tree_strategy)
    full_run_time = (int(time.time_ns()) - full_run_time) / 1000000000

    # run partial trees
    partial_run_time = int(time.time_ns())
    partial_run_result = run_stands(stands, simulation_declaration, run_partial_tree_strategy)
    partial_run_time = (int(time.time_ns()) - partial_run_time) / 1000000000
    print_run_result(full_run_result)
    print_run_result(partial_run_result)
    print("Full tree run in    {}".format(full_run_time))
    print("Partial tree run in {}".format(partial_run_time))


if __name__ == "__main__":
    main()
