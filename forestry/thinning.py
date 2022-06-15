import forestry.forestry_utils as futil
from collections import OrderedDict
from forestdatamodel.model import ForestStand
from typing import Tuple, Callable
from forestry.thinning_limits import get_thinning_bounds, get_first_thinning_residue
from forestry.aggregate_utils import store_operation_aggregate, get_operation_aggregates, get_latest_operation_aggregate


def evaluate_thinning_conditions(predicates):
    return all(f() for f in predicates)


def thinning_from_above(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    factor = operation_parameters['thinning_factor']

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)

    (lower_limit, upper_limit) = get_thinning_bounds(stand)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thin_condition = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand)
        new_stand, new_aggregate = thinning(stand, factor, thin_condition)
    else:
        raise UserWarning("Unable to perform thinning from below")
    return new_stand,  store_operation_aggregate(simulation_aggregates, new_aggregate, 'thinning_from_above')


def thinning_from_below(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    factor = operation_parameters['thinning_factor']

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)

    (lower_limit, upper_limit) = get_thinning_bounds(stand)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thin_condition = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand)
        new_stand, new_aggregate = thinning(stand, factor, thin_condition)
    else:
        raise UserWarning("Unable to perform thinning from below")
    return new_stand,  store_operation_aggregate(simulation_aggregates, new_aggregate, 'thinning_from_below')


def thinning(stand: ForestStand, thinning_factor: float, thin_predicate: Callable) -> Tuple[ForestStand, dict]:
    n = len(stand.reference_trees)
    c = thinning_factor
    stems_removed = 0.0
    while thin_predicate(stand):
        # cut until lower bound reached
        for i, rt in enumerate(stand.reference_trees):
            thin_factor = (1.0-c)/n * i + c
            thin_factor = 1.0 if thin_factor > 1.0 else thin_factor
            new_stems_per_ha = rt.stems_per_ha * thin_factor
            stems_removed += rt.stems_per_ha - new_stems_per_ha
            rt.stems_per_ha = new_stems_per_ha
    new_aggregate = { 'stems_removed': stems_removed }
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
