import forestry.forestry_utils as futil
from collections import OrderedDict
from forestdatamodel.model import ForestStand
from typing import Tuple
from forestry.thinning_limits import get_thinning_bounds
from forestry.aggregate_utils import store_operation_aggregate, get_operation_aggregates, get_latest_operation_aggregate


def thinning_from_below(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)
    new_stand, new_aggregate = thinning( (stand, simulation_aggregates), **operation_parameters )
    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'thinning_from_below')
    return new_stand, new_simulation_aggregates


def thinning_from_above(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)
    new_stand, new_aggregate = thinning( (stand, simulation_aggregates), **operation_parameters )
    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'thinning_from_above')
    return new_stand, new_simulation_aggregates


def thinning(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    time_point = simulation_aggregates['current_time_point']
    operation_tag = simulation_aggregates['current_operation_tag']

    # solve basal area lower and upper bound
    (lower_basal_area, upper_basal_area) = get_thinning_bounds(stand)
    new_aggregate = { 'stems_removed': 0.0 }
    if upper_basal_area <= futil.overall_basal_area(stand):
        # thinning enabled
        n = len(stand.reference_trees)
        c = operation_parameters['c']
        e = operation_parameters['e']
        stems_removed = 0.0
        while (lower_basal_area + e) < futil.overall_basal_area(stand):
            # cut until lower bound reached
            for i, rt in enumerate(stand.reference_trees):
                thin_factor = (1.0-c)/n * i + c
                thin_factor = 1.0 if thin_factor > 1.0 else thin_factor
                new_stems_per_ha = rt.stems_per_ha * thin_factor
                stems_removed += rt.stems_per_ha - new_stems_per_ha
                rt.stems_per_ha = new_stems_per_ha
        new_aggregate = { 'stems_removed': stems_removed }
    else:
        # unable to thin, stop variant simulation
        raise UserWarning("unable to perform operation {}, at time point {} basal area upper bound not reached"
            .format(operation_tag, time_point))


    return (stand, new_aggregate)


def report_overall_removal(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    _, simulation_aggregates = payload
    operation_tags = operation_parameters['thinning_method']

    report_removal_collection = {}
    for tag in operation_tags:
        thinning_aggregates = get_operation_aggregates(simulation_aggregates, tag)
        if thinning_aggregates is None:
            new_aggregate = 0.0
        else:
            s = sum( x['stems_removed'] for x in thinning_aggregates.values() )
            new_aggregate = s
        report_removal_collection[tag] = new_aggregate

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, report_removal_collection, 'report_overall_removal')

    return _, new_simulation_aggregates