from collections.abc import Callable
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.collected_types import CrossCuttableTree
from lukefi.metsi.domain.forestry_operations.thinning_limits import (
    resolve_thinning_bounds, resolve_first_thinning_residue)
from lukefi.metsi.forestry.harvest import thinning
from lukefi.metsi.forestry import forestry_utils as futil
from lukefi.metsi.sim.core_types import CollectedData, OpTuple


def evaluate_thinning_conditions(predicates):
    return all(f() for f in predicates)


def iterative_thinning_with_output(
    stand: ForestStand,
    collected_data: CollectedData,
    thinning_factor: float,
    thin_predicate: Callable[[ForestStand], bool],
    extra_factor_solver: Callable[[int, int, float], float],
    tag: str,
) -> OpTuple[ForestStand]:
    """Run iterative thinning and save output for trees that had their stem count reduced.
    No output is written for unchanged trees."""
    f0 = [t.stems_per_ha for t in stand.reference_trees]
    stand = thinning.iterative_thinning(stand, thinning_factor, thin_predicate, extra_factor_solver)

    thinning_output = [
        CrossCuttableTree(
            f-t.stems_per_ha,
            t.species,
            t.breast_height_diameter,
            t.height,
            'harvested',
            tag,
            collected_data.current_time_point
        )
        for t, f in zip(stand.reference_trees, f0)
        if f > t.stems_per_ha
    ]

    collected_data.extend_list_result("felled_trees", thinning_output)

    return stand, collected_data


def first_thinning(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    stand, collected_data = input_
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform first thinning. No trees exist.")
    epsilon = operation_parameters['e']
    hdom_0 = operation_parameters['dominant_height_lower_bound']
    hdom_n = operation_parameters['dominant_height_upper_bound']
    hdom_0 = 11 if hdom_0 is None else hdom_0
    hdom_n = 16 if hdom_n is None else hdom_n

    residue_stems = resolve_first_thinning_residue(stand)

    def stems_over_limit():
        return residue_stems < futil.overall_stems_per_ha(stand.reference_trees)

    def hdom_in_between():
        return hdom_0 <= futil.solve_dominant_height_c_largest(stand) <= hdom_n

    predicates = [stems_over_limit, hdom_in_between]

    if evaluate_thinning_conditions(predicates):
        stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)
        return iterative_thinning_with_output(
            stand=stand,
            collected_data=collected_data,
            thinning_factor=operation_parameters['thinning_factor'],
            thin_predicate=lambda s: (residue_stems + epsilon) <= futil.overall_stems_per_ha(s.reference_trees),
            extra_factor_solver=lambda i, n, c: (1.0-c) * i/n,
            tag='first_thinning',
        )
    else:
        raise UserWarning("Unable to perform first thinning")


def thinning_from_above(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    stand, collected_data = input_
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform thinning from above. No trees exist.")
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    def upper_limit_reached(): return upper_limit < futil.overall_basal_area(stand.reference_trees)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        return iterative_thinning_with_output(
            stand=stand,
            collected_data=collected_data,
            thinning_factor=operation_parameters['thinning_factor'],
            thin_predicate=lambda s: (lower_limit + epsilon) <= futil.overall_basal_area(s.reference_trees),
            extra_factor_solver=lambda i, n, c: (1.0-c) * i/n,
            tag='thinning_from_above',
        )
    else:
        raise UserWarning("Unable to perform thinning from above")


def thinning_from_below(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    stand, collected_data = input_
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform thinning from below. No trees exist.")
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)

    def upper_limit_reached():
        return upper_limit < futil.overall_basal_area(stand.reference_trees)

    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        return iterative_thinning_with_output(
            stand=stand,
            collected_data=collected_data,
            thinning_factor=operation_parameters['thinning_factor'],
            thin_predicate=lambda s: (lower_limit + epsilon) <= futil.overall_basal_area(s.reference_trees),
            extra_factor_solver=lambda i, n, c: (1.0-c) * i/n,
            tag='thinning_from_below',
        )
    else:
        raise UserWarning("Unable to perform thinning from below")


def even_thinning(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    stand, collected_data = input_
    if len(stand.reference_trees) == 0:
        raise UserWarning("Unable to perform even thinning. No trees exist.")
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)

    def upper_limit_reached():
        return upper_limit < futil.overall_basal_area(stand.reference_trees)
    
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        return iterative_thinning_with_output(
            stand=stand,
            collected_data=collected_data,
            thinning_factor=operation_parameters['thinning_factor'],
            thin_predicate=lambda s: (lower_limit + epsilon) <= futil.overall_basal_area(s.reference_trees),
            extra_factor_solver=lambda i, n, c: 0,
            tag='even_thinning',
        )
    else:
        raise UserWarning("Unable to perform even thinning")


def report_overall_removal(payload: OpTuple, **operation_parameters) -> OpTuple:
    _, collected_data = payload
    operation_tags = operation_parameters['thinning_method']

    report_removal_collection = {}
    for tag in operation_tags:
        thinning_collection = [x for x in collected_data.get_list_result("felled_trees") if x.operation == tag]
        if thinning_collection is None:
            new_sum = 0.0
        else:
            new_sum = sum(y.stems_per_ha for y in thinning_collection)
        report_removal_collection[tag] = new_sum
    collected_data.store('report_overall_removal', report_removal_collection)
    return payload
