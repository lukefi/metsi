from collections.abc import Callable
from copy import deepcopy
from lukefi.metsi.sim.core_types import OperationPayload, SimConfiguration, EventTree
from lukefi.metsi.sim.generators import full_tree_generators, compose_nested, partial_tree_generators_by_time_point


def evaluate_sequence[T](payload: T, *operations: Callable[[T], T]) -> T:
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


def run_chains_iteratively(payload, chains: list[list[Callable]]) -> list:
    """Execute all given operation chains for the given state payload. Return the collection of success results from
    all chains.

    :param payload: a simulation state payload
    :param chains: list of a list of functions usable to process the payload
    :return: list of success results of applying the function chains on the payload"""
    results = []
    for chain in chains:
        try:
            results.append(evaluate_sequence(deepcopy(payload), *chain))
        except UserWarning:
            ...
            # TODO aborted run reporting
    return results


def chain_evaluator(payload: OperationPayload, root_node: EventTree) -> list[OperationPayload]:
    chains = root_node.operation_chains()
    return run_chains_iteratively(payload, chains)


def depth_first_evaluator(payload: OperationPayload, root_node: EventTree) -> list[OperationPayload]:
    return root_node.evaluate(payload)


def run_full_tree_strategy[T](payload: OperationPayload[T], config: SimConfiguration,
                              evaluator=chain_evaluator) -> list[OperationPayload[T]]:
    """Process the given operation payload using a simulation state tree created from the declaration. Full simulation
    tree and operation chains are pre-generated for the run. This tree strategy creates the full theoretical branching
    tree for the simulation, carrying a significant memory and runtime overhead for large trees.

    :param payload: a simulation state payload
    :param config: a prepared SimConfiguration object
    :param evaluator: a function for performing computation from given EventTree and for given OperationPayload
    :return: a list of resulting simulation state payloads
    """

    nestable_generator = full_tree_generators(config)
    root_node = compose_nested(nestable_generator)
    result = evaluator(payload, root_node)
    return result


def run_partial_tree_strategy[T](payload: OperationPayload[T], config: SimConfiguration,
                                 evaluator=chain_evaluator) -> list[OperationPayload[T]]:
    """Process the given operation payload using a simulation state tree created from the declaration. The simulation
    tree and operation chains are generated and executed in order per simulation time point. This reduces the amount of
    redundant, always-failing operation chains and redundant branches of the simulation tree.

    :param payload: a simulation state payload
    :param config: a prepared SimConfiguration object
    :param evaluator: a function for performing computation from given EventTree and for given OperationPayload
    :return: a list of resulting simulation state payloads
    """
    generators_by_time_point = partial_tree_generators_by_time_point(config)
    root_nodes = {}
    results = [payload]

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
