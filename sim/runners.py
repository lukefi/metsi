from typing import Optional, Callable, List
from copy import deepcopy

import forestry.operations
from sim.core_types import Step, OperationPayload, SimulationParams
from sim.generators import full_tree_generators_from_declaration, compose, tree_generators_by_time_point


def evaluate_sequence(payload, *operations: Callable) -> Optional:
    """
    Compute a single processing result for single data input.

    Execute all given instruction functions, chaining the input_data argument and
    iterative results as arguments to subsequent calls. Abort on any function raising an exception.

    :param payload: argument for the first instruction functions
    :param operations: *arg list of operation functions to execute in order
    :raises Exception: on any instruction function raising, catch and propagate the exception
    :return: return value of the last instruction function
    """
    result = None
    current = payload
    for func in operations:
        result = func(current)
        current = result
    return result


def run_chains_iteratively(payload, chains: List[List[Callable]]) -> List:
    results = []
    for chain in chains:
        try:
            results.append(evaluate_sequence(deepcopy(payload), *chain))
        except UserWarning as e:
            ...
            # TODO aborted run reporting
    return results


def run_full_tree_strategy(payload: OperationPayload, simulation_declaration: dict, operation_lookup: dict) -> List[OperationPayload]:
    full_generators = full_tree_generators_from_declaration(simulation_declaration, operation_lookup)
    tree = compose(*full_generators)
    chains = tree.operation_chains()
    result = run_chains_iteratively(payload, chains)
    return result


def run_partial_tree_strategy(payload: OperationPayload, simulation_declaration: dict, operation_lookup: dict) -> List[OperationPayload]:
    generators_by_time_point = tree_generators_by_time_point(simulation_declaration, operation_lookup)
    chains_by_time_point = {}
    result = [payload]
    for k, v in generators_by_time_point.items():
        chains_by_time_point[k] = compose(*v).operation_chains()

    for time_point in SimulationParams(**simulation_declaration['simulation_params']).simulation_time_series():
        time_point_result: list[OperationPayload] = []
        for payload in result:
            result = run_chains_iteratively(payload, chains_by_time_point[time_point])
            time_point_result.extend(result)
        result = time_point_result
    return result
