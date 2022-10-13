from forestdatamodel.model import ForestStand
from typing import Any, Callable
from forestry.aggregates import CrossCutAggregate, ThinningOutput, TreeThinData
from forestry.thinning_limits import resolve_thinning_bounds, resolve_first_thinning_residue
from forestryfunctions.harvest import thinning
from forestryfunctions.cross_cutting import cross_cutting
from forestryfunctions import forestry_utils as futil
from sim.core_types import AggregatedResults, OpTuple
import numpy as np
from io import StringIO

def evaluate_thinning_conditions(predicates):
    return all(f() for f in predicates)


def get_timber_price_table(csv_string: str) -> np.ndarray:
    """Converts the string representation of a timber price table csv to a numpy.ndarray."""
    table = np.genfromtxt(StringIO(csv_string), delimiter=';', skip_header=1)
    return table
    

def thinning_aux(
    stand: ForestStand,
    aggr: AggregatedResults,
    thinning_factor: float,
    thin_predicate: Callable[[ForestStand], bool],
    extra_factor_solver: Callable[[int, int, float], float],
    tag: str,
    timber_price_table: np.ndarray,
    cross_cut: bool
) -> OpTuple[ForestStand]:
    f0 = [t.stems_per_ha for t in stand.reference_trees]
    stand = thinning.iterative_thinning(stand, thinning_factor, thin_predicate, extra_factor_solver)
    thinning_output = ThinningOutput(removed=[
            TreeThinData(f-t.stems_per_ha, t.species, t.breast_height_diameter, t.height)
            for t,f in zip(stand.reference_trees, f0)
            if f > t.stems_per_ha
        ])

    if cross_cut:
        volumes, values = cross_cutting.cross_cut_thinning_output(thinning_output, stand.area, timber_price_table)
        volumes_sum, values_sum = cross_cutting.calculate_cross_cut_aggregates(volumes, values)
        cc_aggr = CrossCutAggregate(volumes_sum, values_sum)
        thinning_output.cross_cut_result = cc_aggr
        aggr.store(tag, thinning_output)
    else:
        aggr.store(tag, thinning_output)

    return stand, aggr


def first_thinning(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    hdom_0 = operation_parameters['dominant_height_lower_bound']
    hdom_n = operation_parameters['dominant_height_upper_bound']
    cross_cut = operation_parameters.get('cross_cut', True)
    hdom_0 = 11 if hdom_0 is None else hdom_0
    hdom_n = 16 if hdom_n is None else hdom_n

    residue_stems = resolve_first_thinning_residue(stand)

    stems_over_limit = lambda: residue_stems < futil.overall_stems_per_ha(stand)
    hdom_in_between = lambda: hdom_0 <= futil.solve_dominant_height_c_largest(stand) <= hdom_n
    predicates = [stems_over_limit, hdom_in_between]

    if evaluate_thinning_conditions(predicates):
        timber_price_table = get_timber_price_table(operation_parameters["timber_price_table"])
        stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)
        return thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (residue_stems + epsilon) <= futil.overall_stems_per_ha(stand),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'first_thinning',
            timber_price_table = timber_price_table,
            cross_cut=cross_cut
        )
    else:
        raise UserWarning("Unable to perform first thinning")


def thinning_from_above(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)
    cross_cut = operation_parameters.get('cross_cut', True)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter, reverse=True)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        timber_price_table = get_timber_price_table(operation_parameters["timber_price_table"])
        return thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'thinning_from_above',
            timber_price_table=timber_price_table,
            cross_cut=cross_cut
        )
    else:
        raise UserWarning("Unable to perform thinning from above")


def thinning_from_below(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)
    cross_cut = operation_parameters.get('cross_cut', True)

    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        timber_price_table = get_timber_price_table(operation_parameters["timber_price_table"])
        return thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand),
            extra_factor_solver = lambda i, n, c: (1.0-c) * i/n,
            tag = 'thinning_from_below',
            timber_price_table=timber_price_table,
            cross_cut=cross_cut
        )
    else:
        raise UserWarning("Unable to perform thinning from below")


def even_thinning(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = input
    epsilon = operation_parameters['e']
    thinning_limits = operation_parameters.get('thinning_limits', None)
    cross_cut = operation_parameters.get('cross_cut', True)

    (lower_limit, upper_limit) = resolve_thinning_bounds(stand, thinning_limits)
    upper_limit_reached = lambda: upper_limit < futil.overall_basal_area(stand)
    predicates = [upper_limit_reached]

    if evaluate_thinning_conditions(predicates):
        timber_price_table = get_timber_price_table(operation_parameters["timber_price_table"])
        return thinning_aux(
            stand = stand,
            aggr = simulation_aggregates,
            thinning_factor = operation_parameters['thinning_factor'],
            thin_predicate = lambda stand: (lower_limit + epsilon) <= futil.overall_basal_area(stand),
            extra_factor_solver = lambda i, n, c: 0,
            tag = 'even_thinning',
            timber_price_table=timber_price_table,
            cross_cut=cross_cut
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
                v.stems_removed_per_ha
                for y in thinning_aggregates.values()
                for v in y.removed
            )
        report_removal_collection[tag] = new_aggregate
    simulation_aggregates.store('report_overall_removal', report_removal_collection)
    return payload
