
from functools import reduce
import forestry.forestry_utils as f_util
from forestry.ForestDataModels import ForestStand
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


def reporting(stand: ForestStand, **operation_parameters) -> ForestStand:
    """This function is an example of how to access the operation specific parameters. Parameter naming is tied to
    simulation control declaration."""
    level = operation_parameters.get('level')
    if level is None:
        print("Stand {} appears normal".format(stand.identifier))
    elif level == 1:
        print("Stand {} appears to be quite green!".format(stand.identifier))
    return stand


def compute_volume(stand: ForestStand) -> float:
    """Debug level function. Does not reflect any real usable model computation.

    Return the sum of the product of basal area and height for all reference trees in the stand"""
    return reduce(lambda acc, cur: f_util.calculate_basal_area(cur) * cur.height, stand.reference_trees, 0.0)


def print_volume(stand: ForestStand) -> ForestStand:
    """Debug level function for printout of timber volume """
    print("stand {} total volume {}".format(stand.identifier, compute_volume(stand)))
    return stand


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'basal_area_thinning': basal_area_thinning,
    'stem_count_thinning': stem_count_thinning,
    'continuous_growth_thinning': continuous_growth_thinning,
    'reporting': reporting,
    'print_volume': print_volume
}


try:
    from forestry.grow_motti import grow_motti
except ImportError:
    # just don't register it when pymotti isn't found.
    # we don't want to make pymotti a required dependency until it's public.
    pass
else:
    operation_lookup['grow_motti'] = grow_motti
