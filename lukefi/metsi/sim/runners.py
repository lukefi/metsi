from collections.abc import Callable
from copy import deepcopy
from typing import TypeVar
from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.app.utils import ConditionFailed
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.collected_data import CollectedData
from lukefi.metsi.sim.event_tree import EventTree
from lukefi.metsi.sim.generators import Generator

from lukefi.metsi.sim.simulation_payload import SimulationPayload
from lukefi.metsi.sim.sim_configuration import SimConfiguration
from lukefi.metsi.sim.state_tree import StateTree

T = TypeVar("T")

Evaluator = Callable[[SimulationPayload[T], EventTree[T]], list[SimulationPayload[T]]]
TreeRunner = Callable[[SimulationPayload[T], SimConfiguration, Evaluator[T]], list[SimulationPayload[T]]]
Runner = Callable[[list[T], SimConfiguration[T], TreeRunner[T], Evaluator[T]], dict[str, list[SimulationPayload[T]]]]


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


def _run_chains_iteratively(payload: T, chains: list[list[Callable[[T], T]]]) -> list[T]:
    """Execute all given operation chains for the given state payload. Return the collection of success results from
    all chains.

    :param payload: a simulation state payload
    :param chains: list of a list of functions usable to process the payload
    :return: list of success results of applying the function chains on the payload"""
    results: list[T] = []
    for chain in chains:
        try:
            results.append(evaluate_sequence(deepcopy(payload), *chain))
        except (ConditionFailed, UserWarning):
            ...
            # TODO aborted run reporting
    return results


def chain_evaluator(payload: SimulationPayload[T], root_node: EventTree[T]) -> list[SimulationPayload[T]]:
    chains = root_node.operation_chains()
    return _run_chains_iteratively(payload, chains)


def depth_first_evaluator(payload: SimulationPayload[T], root_node: EventTree[T]) -> list[SimulationPayload[T]]:
    state_tree: StateTree[PossiblyLayered[T]] = StateTree()
    return root_node.evaluate(payload, state_tree)


def run_full_tree_strategy(payload: SimulationPayload[T], config: SimConfiguration,
                           evaluator: Evaluator[T] = chain_evaluator) -> list[SimulationPayload[T]]:
    """Process the given operation payload using a simulation state tree created from the declaration. Full simulation
    tree and operation chains are pre-generated for the run. This tree strategy creates the full theoretical branching
    tree for the simulation, carrying a significant memory and runtime overhead for large trees.

    :param payload: a simulation state payload
    :param config: a prepared SimConfiguration object
    :param evaluator: a function for performing computation from given EventTree and for given OperationPayload
    :return: a list of resulting simulation state payloads
    """

    nestable_generator: Generator[T] = config.full_tree_generators()
    root_node: EventTree[T] = nestable_generator.compose_nested()
    result = evaluator(payload, root_node)
    return result


def run_partial_tree_strategy(payload: SimulationPayload[T], config: SimConfiguration[T],
                              evaluator: Evaluator[T] = chain_evaluator
                              ) -> list[SimulationPayload[T]]:
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
    results: list[SimulationPayload[T]] = [payload]

    # build chains_by_time_point, which is a dict of chains
    for time_point, nestable_generator in generators_by_time_point.items():
        root_nodes[time_point] = nestable_generator.compose_nested()

    for time_point in config.time_points:
        root_node = root_nodes[time_point]
        time_point_results: list[SimulationPayload[T]] = []
        for payload_ in results:
            payload_results = evaluator(payload_, root_node)
            time_point_results.extend(payload_results)
        results = time_point_results
    return results


def default_runner(units: list[T],
                   config: SimConfiguration[T],
                   formation_strategy: TreeRunner[T],
                   evaluation_strategy: Evaluator[T]) -> dict[str, list[SimulationPayload[T]]]:
    retval: dict[str, list[SimulationPayload[T]]] = {}
    for i, unit in enumerate(units):
        payload = SimulationPayload[T](
            computational_unit=unit,
            collected_data=CollectedData(initial_time_point=config.time_points[0]),
            operation_history=[])

        schedule_payloads = formation_strategy(payload, config, evaluation_strategy)

        print_logline(f"Alternatives for unit {i}: {len(schedule_payloads)}")
        retval[str(i)] = schedule_payloads
    return retval
