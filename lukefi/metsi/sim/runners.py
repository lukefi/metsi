from collections.abc import Callable
from copy import deepcopy
from typing import TypeVar
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.event_tree import EventTree
from lukefi.metsi.sim.generators import (
    Generator,
    compose_nested)
from lukefi.metsi.sim.operation_payload import OperationPayload
from lukefi.metsi.sim.sim_configuration import SimConfiguration
from lukefi.metsi.sim.state_tree import StateTree

T = TypeVar("T")

Evaluator = Callable[[OperationPayload[T], EventTree[T]], list[OperationPayload[T]]]
Runner = Callable[[OperationPayload[T], SimConfiguration, Evaluator[T]], list[OperationPayload[T]]]


def evaluate_sequence(payload: T, *operations: Callable[[T], T]) -> T:
    """
    Compute a single processing result for single data input.

    Execute all given instruction functions, chaining the input_data argument and
    iterative results as arguments to subsequent calls. Abort on any function raising an exception.

    :param payload: argument for the first instruction functions
    :param operations: *arg list of operation functions to execute in order
    :raises Exception: on any instruction function raising, catch and propagate the exception
    :return: return value of the last instruction function
    """
    current = payload
    for func in operations:
        current = func(current)
    return current


def run_chains_iteratively(payload: T, chains: list[list[Callable[[T], T]]]) -> list[T]:
    """Execute all given operation chains for the given state payload. Return the collection of success results from
    all chains.

    :param payload: a simulation state payload
    :param chains: list of a list of functions usable to process the payload
    :return: list of success results of applying the function chains on the payload"""
    results: list[T] = []
    for chain in chains:
        try:
            results.append(evaluate_sequence(deepcopy(payload), *chain))
        except UserWarning:
            ...
            # TODO aborted run reporting
    return results


def chain_evaluator(payload: OperationPayload[T], root_node: EventTree[T]) -> list[OperationPayload[T]]:
    chains = root_node.operation_chains()
    return run_chains_iteratively(payload, chains)


def depth_first_evaluator(payload: OperationPayload[T], root_node: EventTree[T]) -> list[OperationPayload[T]]:
    state_tree: StateTree[PossiblyLayered[T]] = StateTree()
    return root_node.evaluate(payload, state_tree)


def run_full_tree_strategy(payload: OperationPayload[T], config: SimConfiguration,
                           evaluator: Evaluator[T] = chain_evaluator) -> list[OperationPayload[T]]:
    """Process the given operation payload using a simulation state tree created from the declaration. Full simulation
    tree and operation chains are pre-generated for the run. This tree strategy creates the full theoretical branching
    tree for the simulation, carrying a significant memory and runtime overhead for large trees.

    :param payload: a simulation state payload
    :param config: a prepared SimConfiguration object
    :param evaluator: a function for performing computation from given EventTree and for given OperationPayload
    :return: a list of resulting simulation state payloads
    """

    nestable_generator: Generator[T] = config.full_tree_generators()
    root_node: EventTree[T] = compose_nested(nestable_generator)
    result = evaluator(payload, root_node)
    return result


def run_partial_tree_strategy(payload: OperationPayload[T], config: SimConfiguration[T],
                              evaluator: Evaluator[T] = chain_evaluator
                              ) -> list[OperationPayload[T]]:
    """Process the given operation payload using a simulation state tree created from the declaration. The simulation
    tree and operation chains are generated and executed in order per simulation time point. This reduces the amount of
    redundant, always-failing operation chains and redundant branches of the simulation tree.

    :param payload: a simulation state payload
    :param config: a prepared SimConfiguration object
    :param evaluator: a function for performing computation from given EventTree and for given OperationPayload
    :return: a list of resulting simulation state payloads
    """
    generators_by_time_point: dict[int, Generator[T]] = config.partial_tree_generators_by_time_point()
    root_nodes: dict[int, EventTree[T]] = {}
    results: list[OperationPayload[T]] = [payload]

    # build chains_by_time_point, which is a dict of chains
    for time_point, nestable_generator in generators_by_time_point.items():
        root_nodes[time_point] = compose_nested(nestable_generator)

    for time_point in config.time_points:
        root_node = root_nodes[time_point]
        time_point_results: list[OperationPayload] = []
        for payload_ in results:
            payload_results = evaluator(payload_, root_node)
            time_point_results.extend(payload_results)
        results = time_point_results
    return results
