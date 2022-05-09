from functools import reduce
from typing import Tuple
import forestry.forestry_utils as f_util
from forestdatamodel import ForestStand
from forestry.grow_acta import grow_acta


def basal_area_thinning(stand: ForestStand, **operation_parameters) -> ForestStand:
    """This function is a no-op example stub"""
    return stand


def stem_count_thinning(stand: ForestStand, **operation_parameters) -> ForestStand:
    """This function is a no-op example stub"""
    return stand


def continuous_growth_thinning(stand: ForestStand, **operation_parameters) -> ForestStand:
    """This function is a no-op example stub"""
    return stand


def compute_volume(stand: ForestStand) -> float:
    """Debug level function. Does not reflect any real usable model computation.

    Return the sum of the product of basal area and height for all reference trees in the stand"""
    return reduce(lambda acc, cur: f_util.calculate_basal_area(cur) * cur.height, stand.reference_trees, 0.0)


def report_volume(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, previous = input
    result = compute_volume(stand)
    if previous is None:
        return stand, {'growth_volume': 0.0, 'current_volume': result}
    else:
        return stand, {
            'growth_volume': previous['growth_volume'] + result - previous['current_volume'],
            'current_volume': result
        }


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'basal_area_thinning': basal_area_thinning,
    'stem_count_thinning': stem_count_thinning,
    'continuous_growth_thinning': continuous_growth_thinning,
    'report_volume': report_volume
}

try:
    from forestry.grow_motti import grow_motti
except ImportError:
    # just don't register it when pymotti isn't found.
    # we don't want to make pymotti a required dependency until it's public.
    pass
else:
    operation_lookup['grow_motti'] = grow_motti
