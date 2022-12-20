import os
import queue
import multiprocessing
import forestry.sim_ops
import sim.generators
from app.app_io import Mela2Configuration
from app.app_types import ForestOpPayload
from app.console_logging import print_logline
from forestry.forestry_types import StandList
from sim.runners import run_full_tree_strategy, run_partial_tree_strategy
from sim.core_types import AggregatedResults, StrategyRunner, SimConfiguration


def run_strategy_multiprocessing_wrapper(payload: ForestOpPayload, config: SimConfiguration, run_strategy: StrategyRunner,  queue: queue.Queue) -> None:
    """Wrapper function for running a simulation strategy in a multiprocessing context. The result is placed in the given queue"""
    result = run_strategy(payload, config)
    queue.put((payload.simulation_state.identifier, result))


def run_stands(
        stands: StandList, config: SimConfiguration,
        run_strategy: StrategyRunner[ForestOpPayload],
        using_multiprocessing: bool
) -> dict[str, list[ForestOpPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given run strategy. Return the
    results organized into a dict keyed with stand identifiers."""

    retval = {}
    args = [
     (
        ForestOpPayload(
            simulation_state=stand,
            aggregated_results=AggregatedResults(initial_time_point=config.time_points[0]),
            operation_history=[],
        ),
        config
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
            id = result[0]
            schedule_payloads = result[1]
            print_logline(f"Alternatives for stand {id}: {len(schedule_payloads)}")
            retval[id] = schedule_payloads
        return retval

    else:
        for arg in args:
            schedule_payloads = run_strategy(*arg)
            id = arg[0].simulation_state.identifier
            print_logline(f"Alternatives for stand {id}: {len(schedule_payloads)}")
            retval[id] = schedule_payloads
        return retval


def resolve_strategy_runner(source: str) -> StrategyRunner[ForestOpPayload]:
    strategy_map = {
        'full': run_full_tree_strategy,
        'partial': run_partial_tree_strategy
    }

    try:
        return strategy_map[source]
    except Exception:
        raise Exception("Unable to resolve alternatives tree formation strategy '{}'".format(source))


def simulate_alternatives(config: Mela2Configuration, control, stands: StandList):
    simconfig = SimConfiguration(
        operation_lookup=forestry.sim_ops.operation_lookup,
        generator_lookup=sim.generators.GENERATOR_LOOKUP,
        **control)
    strategy_runner = resolve_strategy_runner(config.strategy)
    result = run_stands(stands, simconfig, strategy_runner, config.multiprocessing)
    return result
