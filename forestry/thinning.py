from collections import OrderedDict
from forestdatamodel.model import ForestStand
from typing import Tuple, Callable
from forestry.thinning_limits import resolve_thinning_bounds, resolve_first_thinning_residue
from forestry.aggregate_utils import store_operation_aggregate, get_operation_aggregates, get_latest_operation_aggregate
from forestryfunctions.harvest import thinning
from forestryfunctions import forestry_utils as futil


def evaluate_thinning_conditions(predicates):
    return all(f() for f in predicates)


def first_thinning(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    factor = operation_parameters['thinning_factor']
    hdom_0 = operation_parameters['dominant_height_lower_bound']
    hdom_n = operation_parameters['dominant_height_upper_bound']
    hdom_0 = 11 if hdom_0 is None else hdom_0
    hdom_n = 16 if hdom_n is None else hdom_n

    residue_stems = resolve_first_thinning_residue(stand)

    stems_over_limit = lambda: residue_stems < futil.overall_stems_per_ha(stand)
    hdom_in_between = lambda: hdom_0 <= futil.solve_dominant_height_c_largest(stand) <= hdom_n
    predicates = [stems_over_limit, hdom_in_between]

    if evaluate_thinning_conditions(predicates):
        stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)
        stop_condition = lambda stand: (residue_stems + epsilon) <= futil.overall_stems_per_ha(stand)
        extra_factor_solver = lambda i, n, c: (1.0-c) * i/n
        new_stand, new_aggregate = thinning.iterative_thinning(stand, factor, stop_condition, extra_factor_solver)
    else:
        raise UserWarning("Unable to perform first thinning")
    return new_stand, store_operation_aggregate(simulation_aggregates, new_aggregate, 'first_thinning')


def thinning_from_above(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    factor = operation_parameters['thinning_factor']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thin_condition = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand)
        extra_factor_solver = lambda i, n, c: (1.0-c) * i/n
        new_stand, new_aggregate = thinning.iterative_thinning(stand, factor, thin_condition, extra_factor_solver)
    else:
        raise UserWarning("Unable to perform thinning from above")
    return new_stand,  store_operation_aggregate(simulation_aggregates, new_aggregate, 'thinning_from_above')


def thinning_from_below(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    factor = operation_parameters['thinning_factor']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thin_condition = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand)
        extra_factor_solver = lambda i, n, c: (1.0-c) * i/n
        new_stand, new_aggregate = thinning.iterative_thinning(stand, factor, thin_condition, extra_factor_solver)
    else:
        raise UserWarning("Unable to perform thinning from below")
    return new_stand,  store_operation_aggregate(simulation_aggregates, new_aggregate, 'thinning_from_below')


def even_thinning(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    factor = operation_parameters['thinning_factor']
    thinning_limits = operation_parameters.get('thinning_limits', None)


    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thin_condition = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand)
        extra_factor_solver = lambda i, n, c: 0
        new_stand, new_aggregate = thinning.iterative_thinning(stand, factor, thin_condition, extra_factor_solver)
    else:
        raise UserWarning("Unable to perform even thinning")
    return new_stand,  store_operation_aggregate(simulation_aggregates, new_aggregate, 'even_thinning')


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
