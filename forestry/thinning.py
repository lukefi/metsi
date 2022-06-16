import forestry.forestry_utils as futil
from collections import OrderedDict
from forestdatamodel.model import ForestStand
from typing import Tuple
from forestry.thinning_limits import get_thinning_bounds
from forestry.aggregate_utils import store_operation_aggregate, get_operation_aggregates, get_latest_operation_aggregate


def thinning_from_below(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = input
    operation_tag = 'thinning_from_below'
    time_point = simulation_aggregates['current_time_point']

    # sort reference trees in increasing order by diameter.
    stand.reference_trees.sort(key=lambda rt: rt.breast_height_diameter)
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

    # store number of removed stems to simualtion aggregates
    store_operation_aggregate(simulation_aggregates, new_aggregate, operation_tag)
    return (stand, simulation_aggregates)


def report_removal(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = payload
    thinning_aggregates = get_operation_aggregates(simulation_aggregates, 'thinning_from_below')

    if thinning_aggregates is None:
        new_aggregate = {'overall_stems_removed': 0.0}
    else:
        s = sum( x['stems_removed'] for x in thinning_aggregates.values() )
        new_aggregate = {'overall_stems_removed': s}

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'report_removal')
    return stand, new_simulation_aggregates
