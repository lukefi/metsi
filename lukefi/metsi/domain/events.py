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
from lukefi.metsi.domain.forestry_types import ForestCondition
from lukefi.metsi.domain.natural_processes.grow_acta import grow_acta
from lukefi.metsi.domain.natural_processes.grow_metsi import grow_metsi
from lukefi.metsi.domain.natural_processes.grow_motti_dll import grow_motti_dll
from lukefi.metsi.domain.natural_processes.grow_motti_dll_vec import grow_motti_dll_vec
from lukefi.metsi.sim.generators import Event
from lukefi.metsi.sim.operations import do_nothing


class Planting(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=planting,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class CrossCutStandingTrees(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=cross_cut_standing_trees,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class CollectStandingTreeProperties(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=collect_standing_tree_properties,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class CalculateNpv(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=calculate_npv,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class CalculateBiomass(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=calculate_biomass,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class ReportState(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=report_state,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class DoNothing(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=do_nothing,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class FirstThinning(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=first_thinning,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class EvenThinning(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=even_thinning,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class Clearcutting(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=clearcutting,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class CrossCutFelledTrees(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=cross_cut_felled_trees,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class CollectFelledTreeProperties(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=collect_felled_tree_properties,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class ReportPeriod(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=report_period,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class ReportCollectives(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=report_collectives,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class GrowActa(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=grow_acta,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class GrowMetsi(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=grow_metsi,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class GrowMotti(Event[ForestStand]):
    def __init__(self, vectorized: bool = False,
                 parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=grow_motti_dll_vec if vectorized else grow_motti_dll,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class ThinningFromBelow(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=thinning_from_below,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


class ThinningFromAbove(Event[ForestStand]):
    def __init__(self, parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[ForestCondition]] = None,
                 postconditions: Optional[list[ForestCondition]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        super().__init__(treatment=thinning_from_above,
                         parameters=parameters,
                         preconditions=preconditions,
                         postconditions=postconditions,
                         file_parameters=file_parameters)


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
