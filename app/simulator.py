import os
import queue
from typing import List, Callable, Dict
import multiprocessing
import forestry.operations
from app.logging import print_logline
from sim.runners import run_full_tree_strategy, run_partial_tree_strategy
from sim.core_types import AggregatedResults, OperationPayload
from forestdatamodel.model import ForestStand


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


def simulate_alternatives(config, control, stands):
    strategy_runner = resolve_strategy_runner(config.strategy)
    result = run_stands(stands, control, strategy_runner, config.multiprocessing)
    return result
