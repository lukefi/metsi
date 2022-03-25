from typing import Optional, Callable, List
from copy import deepcopy

from sim.core_types import Step, OperationPayload


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
