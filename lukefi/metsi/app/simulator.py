from lukefi.metsi.data.layered_model import LayeredObject
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum

from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.app_types import ForestOpPayload
from lukefi.metsi.app.metsi_enum import FormationStrategy, EvaluationStrategy
from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.sim.runners import (
    run_full_tree_strategy,
    run_partial_tree_strategy,
    depth_first_evaluator,
    chain_evaluator)
from lukefi.metsi.sim.core_types import CollectedData, Runner, SimConfiguration, Evaluator
from lukefi.metsi.app.utils import MetsiException


def run_stands(stands: StandList,
               config: SimConfiguration,
               runner: Runner[ForestOpPayload],
               evaluator: Evaluator[ForestOpPayload]) -> dict[str, list[ForestOpPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given runner. Return the
    results organized into a dict keyed with stand identifiers."""

    retval: dict[str, list[ForestOpPayload]] = {}
    for stand in stands:
        overlaid_stand = LayeredObject[ForestStand](stand)
        overlaid_stand.reference_trees = [LayeredObject[ReferenceTree](tree) for tree in overlaid_stand.reference_trees]
        overlaid_stand.tree_strata = [LayeredObject[TreeStratum](stratum) for stratum in overlaid_stand.tree_strata]
        payload = ForestOpPayload(
            computational_unit=overlaid_stand,
            collected_data=CollectedData(initial_time_point=config.time_points[0]),
            operation_history=[],
        )
        schedule_payloads = runner(payload, config, evaluator)
        identifier = stand.identifier
        print_logline(f"Alternatives for stand {identifier}: {len(schedule_payloads)}")
        retval[identifier] = schedule_payloads
    return retval


def resolve_formation_strategy(source: FormationStrategy) -> Runner[ForestOpPayload]:
    formation_strategy_map: dict[FormationStrategy, Runner[ForestOpPayload]] = {
        FormationStrategy.FULL: run_full_tree_strategy,
        FormationStrategy.PARTIAL: run_partial_tree_strategy
    }

    if source in formation_strategy_map:
        return formation_strategy_map[source]
    raise MetsiException(f"Unable to resolve event tree formation strategy '{source}'")


def resolve_evaluation_strategy(source: EvaluationStrategy) -> Evaluator[ForestOpPayload]:
    evaluation_strategy_map: dict[EvaluationStrategy, Evaluator[ForestOpPayload]] = {
        EvaluationStrategy.DEPTH: depth_first_evaluator,
        EvaluationStrategy.CHAINS: chain_evaluator
    }

    if source in evaluation_strategy_map:
        return evaluation_strategy_map[source]
    raise MetsiException(f"Unable to resolve event tree evaluation strategy '{source}'")


def simulate_alternatives(config: MetsiConfiguration, control, stands: StandList):
    simconfig = SimConfiguration(**control)
    formation_strategy = resolve_formation_strategy(config.formation_strategy)
    evaluation_strategy = resolve_evaluation_strategy(config.evaluation_strategy)
    result = run_stands(stands, simconfig, formation_strategy, evaluation_strategy)
    return result
