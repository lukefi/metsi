from typing import Any
from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.metsi_enum import FormationStrategy, EvaluationStrategy
from lukefi.metsi.sim.runners import (
    Runner,
    default_runner,
    run_full_tree_strategy,
    run_partial_tree_strategy,
    depth_first_evaluator,
    chain_evaluator)
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.sim.runners import Evaluator
from lukefi.metsi.sim.runners import TreeRunner
from lukefi.metsi.sim.sim_configuration import SimConfiguration

_FORMATION_STRATEGY_MAP: dict[FormationStrategy, TreeRunner] = {
    FormationStrategy.FULL: run_full_tree_strategy,
    FormationStrategy.PARTIAL: run_partial_tree_strategy
}

_EVALUATION_STRATEGY_MAP: dict[EvaluationStrategy, Evaluator] = {
    EvaluationStrategy.DEPTH: depth_first_evaluator,
    EvaluationStrategy.CHAINS: chain_evaluator
}


def simulate_alternatives[T](config: MetsiConfiguration,
                             control: dict[str, Any],
                             stands: list[T],
                             runner: Runner[T] = default_runner):
    simconfig = SimConfiguration[T](**control)
    formation_strategy = _resolve_formation_strategy(config.formation_strategy)
    evaluation_strategy = _resolve_evaluation_strategy(config.evaluation_strategy)
    result = runner(stands, simconfig, formation_strategy, evaluation_strategy)
    return result


def _resolve_formation_strategy(source: FormationStrategy) -> TreeRunner:
    if source in _FORMATION_STRATEGY_MAP:
        return _FORMATION_STRATEGY_MAP[source]
    raise MetsiException(f"Unable to resolve event tree formation strategy '{source}'")


def _resolve_evaluation_strategy(source: EvaluationStrategy) -> Evaluator:
    if source in _EVALUATION_STRATEGY_MAP:
        return _EVALUATION_STRATEGY_MAP[source]
    raise MetsiException(f"Unable to resolve event tree evaluation strategy '{source}'")
