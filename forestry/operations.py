from forestryfunctions import forestry_utils as futil
from functools import reduce
from collections import OrderedDict
from typing import Tuple
from forestdatamodel.model import ForestStand
from forestry.grow_acta import grow_acta
from forestry.r_utils import lmfor_volume
from forestry.thinning import first_thinning, thinning_from_above, thinning_from_below, report_overall_removal, \
    even_thinning
from forestry.aggregate_utils import store_operation_aggregate, get_latest_operation_aggregate
from forestry.cross_cutting import cross_cut_stand, calculate_cross_cut_aggregates
from sim.core_types import OperationPayload


def compute_volume(stand: ForestStand) -> float:
    """Debug level function. Does not reflect any real usable model computation.

    Return the sum of the product of basal area and height for all reference trees in the stand"""
    return reduce(lambda acc, cur: futil.calculate_basal_area(cur) * cur.height, stand.reference_trees, 0.0)


def report_volume(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = payload
    latest_aggregate = get_latest_operation_aggregate(simulation_aggregates, 'report_volume')

    volume_function = compute_volume
    if operation_parameters.get('lmfor_volume'):
        volume_function = lmfor_volume
    result = volume_function(stand)

    if latest_aggregate is None:
        new_aggregate = {'growth_volume': 0.0, 'current_volume': result}
    else:
        new_aggregate = {
            'growth_volume': latest_aggregate['growth_volume'] + result - latest_aggregate['current_volume'],
            'current_volume': result
        }

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'report_volume')

    return stand, new_simulation_aggregates


def cross_cut(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    """
    This is the entry point for calculating cross cut (apteeraus) value and volume.
    """

    stand, simulation_aggregates = payload

    volumes, values = cross_cut_stand(stand)

    total_volume, total_value = calculate_cross_cut_aggregates(volumes, values)

    new_aggregate = {
        'cross_cut_volume': total_volume,
        'cross_cut_value': total_value
    }

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'report_cross_cutting')

    result = (stand, new_simulation_aggregates)
    return result


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'thinning_from_below': thinning_from_below,
    'thinning_from_above': thinning_from_above,
    'first_thinning': first_thinning,
    'even_thinning': even_thinning,
    'report_volume': report_volume,
    'report_overall_removal': report_overall_removal,
    'cross_cut': cross_cut
}

try:
    from forestry.grow_motti import grow_motti
except ImportError:
    # just don't register it when pymotti isn't found.
    # we don't want to make pymotti a required dependency until it's public.
    pass
else:
    operation_lookup['grow_motti'] = grow_motti
