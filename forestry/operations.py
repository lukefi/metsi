from enum import Enum
from importlib import import_module
from itertools import repeat
from functools import reduce, cache
from typing import Any

from forestdatamodel.model import ForestStand
from forestry.aggregates import BiomassAggregate, VolumeAggregate
from forestryfunctions import forestry_utils as futil
from forestryfunctions.r_utils import lmfor_volume
from forestry.biomass_repola import biomasses_by_component_stand
from forestry.cross_cutting import cross_cut_felled_trees, cross_cut_standing_trees
from forestry.grow_acta import grow_acta
from forestry.thinning import first_thinning, thinning_from_above, thinning_from_below, report_overall_removal, \
    even_thinning
from forestry.collectives import autocollective, getvarfn, collect_all
from sim.core_types import OpTuple
from sim.operations import T
from forestry.net_present_value import calculate_npv
from forestry.clearcut import clearcutting
from forestry.planting import planting


def compute_volume(stand: ForestStand) -> float:
    """Debug level function. Does not reflect any real usable model computation.

    Return the sum of the product of basal area and height for all reference trees in the stand"""
    return reduce(lambda acc, cur: futil.calculate_basal_area(cur) * cur.height, stand.reference_trees, 0.0)


def report_volume(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = payload
    volume_function = compute_volume
    if operation_parameters.get('lmfor_volume'):
        volume_function = lmfor_volume
    result = volume_function(stand)
    prev = simulation_aggregates.prev('report_volume')
    simulation_aggregates.store(
        'report_volume',
        VolumeAggregate.initial(result) if prev is None
        else VolumeAggregate.from_prev(prev, result),
    )
    return payload


def report_biomass(input: OpTuple[ForestStand], **operation_params) -> OpTuple[ForestStand]:
    """For the given ForestStand, this operation computes and stores the current biomass tonnage and difference to last
    calculation into the aggregate structure."""
    stand, aggregates = input
    models = operation_params.get('model_set', 1)

    # TODO: need proper functionality to find tree volumes, model_set 2
    volumes = list(repeat(100.0, len(stand.reference_trees)))
    # TODO: need proper functionality to find waste volumes, model_set 2
    wastevolumes = list(repeat(100.0, len(stand.reference_trees)))

    biomass = biomasses_by_component_stand(stand, volumes, wastevolumes, models)
    prev = aggregates.prev('report_biomass')
    aggregates.store(
        'report_biomass',
        BiomassAggregate.initial(biomass) if prev is None
        else BiomassAggregate.from_prev(prev, biomass)
    )

    return input


def report_collectives(input: OpTuple[T], /, **collectives: str) -> OpTuple[T]:
    state, aggr = input
    res = _collector_wrapper(
        collectives,
        lambda name: autocollective(getattr(state, name)),
        lambda name: autocollective(
            aggr.operation_results[name],
            time_point=[aggr.current_time_point]),
        state = state,
        aggr = aggr.operation_results,
        time = aggr.current_time_point
        )
    aggr.store('report_collectives', res)
    return input


def report_state(input: OpTuple[T], /, **operation_parameters: str) -> OpTuple[T]:
    state, aggr = input
    res = _collector_wrapper(
        operation_parameters,
        lambda name: autocollective(getattr(state, name)),
        lambda name: autocollective(
            aggr.operation_results[name],
            time_point=[aggr.current_time_point]),
        state=state
    )
    aggr.store('report_state', res)
    return input


def property_collector(objects: list[object], properties: list[str]) -> list[list]:
    result_rows = []
    for o in objects:
        row = []
        for p in properties:
            if not hasattr(o, p):
                raise Exception(f"Unknown property {p} in {o.__class__}")
            val = o.__getattribute__(p) or 0.0
            if isinstance(val, Enum):
                val = val.value
            row.append(val)
        result_rows.append(row)
    return result_rows


def collect_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, aggr = input
    output_name = operation_parameters.get('output_name', 'collect_properties')
    result_rows = []
    if not len(operation_parameters):
        return input
    for key, properties in operation_parameters.items():
        objects: list[object]
        if isinstance(properties, str):
            properties = [properties]
        elif not isinstance(properties, list):
            raise Exception(f"Properties to collect must be a list of strings or a single string for {key}")
        if key == "stand":
            objects = [stand]
        elif key == "tree":
            objects = stand.reference_trees
        elif key == "stratum":
            objects = stand.tree_strata
        else:
            objects = list(filter(lambda obj: obj.time_point == aggr.current_time_point, aggr.get_list_result(key)))
        collected = property_collector(objects, properties)
        result_rows.extend(collected)
    aggr.store(output_name, result_rows)
    return stand, aggr


def collect_standing_tree_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    properties = operation_parameters.get("properties")
    return collect_properties(input, tree=properties, output_name="collect_standing_tree_properties")


def collect_felled_tree_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    properties = operation_parameters.get("properties")
    return collect_properties(input, felled_trees=properties, output_name="collect_felled_tree_properties")


def report_period(input: OpTuple[T], /, **operation_parameters: str) -> OpTuple[T]:
    _, aggr = input
    last_period = aggr.prev('report_period')
    t0 = aggr.initial_time_point if last_period is None else list(aggr.get('report_period').keys())[-1]
    res = _collector_wrapper(
        operation_parameters,
        lambda name: autocollective(
            aggr.operation_results[name],
            time_point=range(t0, aggr.current_time_point)
        )
    )
    aggr.store('report_period', res)
    return input


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'thinning_from_below': thinning_from_below,
    'thinning_from_above': thinning_from_above,
    'first_thinning': first_thinning,
    'even_thinning': even_thinning,
    'planting': planting,
    'clearcutting': clearcutting,
    'report_biomass': report_biomass,
    'report_volume': report_volume,
    'report_overall_removal': report_overall_removal,
    'cross_cut_felled_trees': cross_cut_felled_trees,
    'cross_cut_standing_trees': cross_cut_standing_trees,
    'report_collectives': report_collectives,
    'report_state': report_state,
    'collect_properties': collect_properties,
    'collect_standing_tree_properties': collect_standing_tree_properties,
    'collect_felled_tree_properties': collect_felled_tree_properties,
    'report_period': report_period,
    'calculate_npv': calculate_npv
}

def try_register(mod: str, func: str):
    try:
        operation_lookup[func] = getattr(import_module(mod), func)
    except ImportError:
        pass

# only register grow_motti when pymotti is installed

try_register("forestry.grow_motti", "grow_motti")

# only register grow_fhk when fhk is installed

try_register("forestry.grow_fhk", "grow_fhk")


def _collector_wrapper(operation_parameters, *aliases, **named_aliases) -> dict[str, Any]:
    getvar = cache(getvarfn(*aliases, **named_aliases))
    return collect_all(operation_parameters, getvar=getvar)
