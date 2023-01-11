import os
import queue
import multiprocessing
import lukefi.metsi.domain.sim_ops
import lukefi.metsi.sim.generators
from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.app_types import ForestOpPayload
from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.sim.runners import run_full_tree_strategy, run_partial_tree_strategy, depth_first_evaluator, \
    chain_evaluator
from lukefi.metsi.sim.core_types import CollectedData, StrategyRunner, SimConfiguration, Evaluator


def run_strategy_multiprocessing_wrapper(payload: ForestOpPayload, config: SimConfiguration, runner: StrategyRunner, evaluator: Evaluator, queue: queue.Queue) -> None:
    """Wrapper function for running a simulation strategy in a multiprocessing context. The result is placed in the given queue"""
    result = runner(payload, config, evaluator)
    queue.put((payload.computational_unit.identifier, result))


def run_stands(
        stands: StandList, config: SimConfiguration,
        runner: StrategyRunner[ForestOpPayload],
        evaluator: Evaluator[ForestOpPayload],
        using_multiprocessing: bool
) -> dict[str, list[ForestOpPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given run strategy. Return the
    results organized into a dict keyed with stand identifiers."""

    retval = {}
    args = [
     (
        ForestOpPayload(
            computational_unit=stand,
            collected_data=CollectedData(initial_time_point=config.time_points[0]),
            operation_history=[],
        ),
        config,
        evaluator
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
            mp_args.append(arg + (runner, evaluator, queue,))

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
            schedule_payloads = runner(*arg)
            id = arg[0].computational_unit.identifier
            print_logline(f"Alternatives for stand {id}: {len(schedule_payloads)}")
            retval[id] = schedule_payloads
        return retval


def resolve_step_strategy(source: str) -> StrategyRunner[ForestOpPayload]:
    step_strategy_map = {
        'full': run_full_tree_strategy,
        'partial': run_partial_tree_strategy
    }

    try:
        return step_strategy_map[source]
    except Exception:
        raise Exception("Unable to resolve step tree formation strategy '{}'".format(source))


def resolve_evaluation_strategy(source: str) -> Evaluator[ForestOpPayload]:
    evaluation_strategy_map = {
        'depth': depth_first_evaluator,
        'chains': chain_evaluator
    }

    try:
        return evaluation_strategy_map[source]
    except Exception:
        raise Exception("Unable to resolve step tree evaluation strategy '{}'".format(source))



def simulate_alternatives(config: MetsiConfiguration, control, stands: StandList):
    simconfig = SimConfiguration(
        operation_lookup=lukefi.metsi.domain.sim_ops.operation_lookup,
        generator_lookup=lukefi.metsi.sim.generators.GENERATOR_LOOKUP,
        **control)
    step_strategy = resolve_step_strategy(config.formation_strategy)
    evaluation_strategy = resolve_evaluation_strategy(config.evaluation_strategy)
    result = run_stands(stands, simconfig, step_strategy, evaluation_strategy, config.multiprocessing)
    return result
