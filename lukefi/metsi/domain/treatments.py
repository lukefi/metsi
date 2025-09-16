from typing import Any, Optional
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.data_collection.biomass_repola import calculate_biomass
from lukefi.metsi.domain.data_collection.cross_cutting import cross_cut_felled_trees, cross_cut_standing_trees
from lukefi.metsi.domain.data_collection.marshalling import (
    collect_felled_tree_properties,
    collect_standing_tree_properties,
    report_collectives,
    report_period,
    report_state)
from lukefi.metsi.domain.data_collection.net_present_value import calculate_npv
from lukefi.metsi.domain.forestry_operations.clearcut import clearcutting
from lukefi.metsi.domain.forestry_operations.planting import planting
from lukefi.metsi.domain.forestry_operations.thinning import (
    even_thinning, first_thinning, thinning_from_above, thinning_from_below)
from lukefi.metsi.domain.natural_processes.grow_acta import grow_acta
from lukefi.metsi.domain.natural_processes.grow_metsi import grow_metsi
from lukefi.metsi.sim.event import Condition
from lukefi.metsi.sim.generators import Treatment
from lukefi.metsi.sim.operations import do_nothing


class Planting(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=planting,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class CrossCutStandingTrees(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=cross_cut_standing_trees,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class CollectStandingTreeProperties(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=collect_standing_tree_properties,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class CalculateNpv(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=calculate_npv,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class CalculateBiomass(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=calculate_biomass,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class ReportState(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=report_state,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class DoNothing(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=do_nothing,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class FirstThinning(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=first_thinning,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class EvenThinning(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=even_thinning,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class Clearcutting(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=clearcutting,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class CrossCutFelledTrees(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=cross_cut_felled_trees,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class CollectFelledTreeProperties(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=collect_felled_tree_properties,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class ReportPeriod(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=report_period,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class ReportCollectives(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=report_collectives,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class GrowActa(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=grow_acta,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class GrowMetsi(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=grow_metsi,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class ThinningFromBelow(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=thinning_from_below,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


class ThinningFromAbove(Treatment[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[ForestStand]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        super().__init__(treatment_fn=thinning_from_above,
                         parameters=parameters,
                         conditions=conditions,
                         file_parameters=file_parameters,
                         run_constraints=run_constraints)


__all__ = [
    "Planting",
    "CrossCutStandingTrees",
    "CollectStandingTreeProperties",
    "CalculateNpv",
    "CalculateBiomass",
    "ReportState",
    "DoNothing",
    "FirstThinning",
    "EvenThinning",
    "Clearcutting",
    "CrossCutFelledTrees",
    "CollectFelledTreeProperties",
    "ReportPeriod",
    "ReportCollectives",
    "GrowActa",
    "GrowMetsi",
    "ThinningFromBelow",
    "ThinningFromAbove",
]
