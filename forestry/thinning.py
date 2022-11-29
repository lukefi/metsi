from forestdatamodel.model import ForestStand
from typing import Any, Callable
from forestryfunctions.cross_cutting.model import CrossCuttableTrees, CrossCuttableTree
from forestry.thinning_limits import resolve_thinning_bounds, resolve_first_thinning_residue
from forestryfunctions.harvest import thinning
from forestryfunctions import forestry_utils as futil
from sim.core_types import AggregatedResults, OpTuple

def evaluate_thinning_conditions(predicates):
    return all(f() for f in predicates)


def iterative_thinning_with_output(
    stand: ForestStand,
    aggr: AggregatedResults,
    thinning_factor: float,
    thin_predicate: Callable[[ForestStand], bool],
    extra_factor_solver: Callable[[int, int, float], float],
    tag: str,
) -> OpTuple[ForestStand]:
    """Run iterative thinning and save output for trees that had their stem count reduced.
    No output is written for unchanged trees."""
    f0 = [t.stems_per_ha for t in stand.reference_trees]
    stand = thinning.iterative_thinning(stand, thinning_factor, thin_predicate, extra_factor_solver)
    thinning_output = CrossCuttableTrees(trees=[
            CrossCuttableTree(f-t.stems_per_ha, t.species, t.breast_height_diameter, t.height)
            for t,f in zip(stand.reference_trees, f0)
            if f > t.stems_per_ha
        ])
    aggr.store(tag, thinning_output)

    return stand, aggr


def first_thinning(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform first thinning. No trees exist.")
    epsilon = operation_parameters['e']
    hdom_0 = operation_parameters['dominant_height_lower_bound']
    hdom_n = operation_parameters['dominant_height_upper_bound']
    hdom_0 = 11 if hdom_0 is None else hdom_0
    hdom_n = 16 if hdom_n is None else hdom_n

    residue_stems = resolve_first_thinning_residue(stand)

    stems_over_limit = lambda: residue_stems < futil.overall_stems_per_ha(stand.reference_trees)
    hdom_in_between = lambda: hdom_0 <= futil.solve_dominant_height_c_largest(stand) <= hdom_n
    predicates = [stems_over_limit, hdom_in_between]

    if evaluate_thinning_conditions(predicates):
        stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)
        return iterative_thinning_with_output(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda s: (residue_stems + epsilon) <= futil.overall_stems_per_ha(s.reference_trees),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'first_thinning',
        )
    else:
        raise UserWarning("Unable to perform first thinning")


def thinning_from_above(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform first thinning. No trees exist.")
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand.reference_trees)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        return iterative_thinning_with_output(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda s: (lower_limit + epsilon) <= futil.overall_basal_area(s.reference_trees),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'thinning_from_above',
        )
    else:
        raise UserWarning("Unable to perform thinning from above")


def thinning_from_below(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform first thinning. No trees exist.")
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand.reference_trees)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        return iterative_thinning_with_output(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda s: (lower_limit + epsilon) <= futil.overall_basal_area(s.reference_trees),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'thinning_from_below',
        )
    else:
        raise UserWarning("Unable to perform thinning from below")


def even_thinning(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform first thinning. No trees exist.")
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand.reference_trees)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        return iterative_thinning_with_output(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda s: (lower_limit + epsilon) <= futil.overall_basal_area(s.reference_trees),
            extra_factor_solver = lambda i, n, c: 0,
            tag = 'even_thinning',
        )
    else:
        raise UserWarning("Unable to perform even thinning")


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
                v.stems_to_cut_per_ha
                for y in thinning_aggregates.values()
                for v in y.trees
            )
        report_removal_collection[tag] = new_aggregate
    simulation_aggregates.store('report_overall_removal', report_removal_collection)
    return payload
