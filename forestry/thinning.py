from forestdatamodel.model import ForestStand
from typing import Any, Callable
from forestry.aggregates import ThinningOutput, TreeThinData
from forestry.thinning_limits import resolve_thinning_bounds, resolve_first_thinning_residue
from forestryfunctions.harvest import thinning
from forestryfunctions import forestry_utils as futil
from sim.core_types import AggregatedResults, OpTuple


def evaluate_thinning_conditions(predicates):
    return all(f() for f in predicates)


def thinning_aux(
    stand: ForestStand,
    aggr: AggregatedResults,
    thinning_factor: float,
    thin_predicate: Callable[[ForestStand], bool],
    extra_factor_solver: Callable[[int, int, float], float],
    tag: str
):
    f0 = [t.stems_per_ha for t in stand.reference_trees]
    thinning.iterative_thinning(stand, thinning_factor, thin_predicate, extra_factor_solver)
    aggr.store(
        tag,
        ThinningOutput([
            TreeThinData(f-t.stems_per_ha, t.species, t.breast_height_diameter, t.height)
            for t,f in zip(stand.reference_trees, f0)
            if f > t.stems_per_ha
        ])
    )


def first_thinning(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
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
        thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (residue_stems + epsilon) <= futil.overall_stems_per_ha(stand),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'first_thinning'
        )
    else:
        raise UserWarning("Unable to perform first thinning")
    return input


def thinning_from_above(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'thinning_from_above'
        )
    else:
        raise UserWarning("Unable to perform thinning from above")
    return input


def thinning_from_below(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'thinning_from_below'
        )
    else:
        raise UserWarning("Unable to perform thinning from below")
    return input


def even_thinning(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)


    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand),
            extra_factor_solver = lambda i, n, c: 0,
            tag = 'even_thinning'
        )
    else:
        raise UserWarning("Unable to perform even thinning")
    return input


def report_overall_removal(payload: OpTuple[Any], **operation_parameters) -> OpTuple[Any]:
    _, simulation_aggregates = payload
    operation_tags = operation_parameters['thinning_method']

    report_removal_collection = {}
    for tag in operation_tags:
        thinning_aggregates = simulation_aggregates.operation_results.get(tag)
        if thinning_aggregates is None:
            new_aggregate = 0.0
        else:
            new_aggregate = sum(
                v.stems_removed_per_ha
                for y in thinning_aggregates.values()
                for v in y.removed
            )
        report_removal_collection[tag] = new_aggregate
    simulation_aggregates.store('report_overall_removal', report_removal_collection)
    return payload
