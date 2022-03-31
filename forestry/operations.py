import math
import itertools
from functools import reduce
import forestry.forestry_utils as f_util
from forestry.ForestDataModels import ForestStand, ReferenceTree


def yearly_diameter_growth_by_species(tree: ReferenceTree, biological_age_aggregate: float, d13_aggregate: float,
                                      height_aggregate: float, dominant_height: float, basal_area_total: float) -> float:
    """ Model source: Acta Forestalia Fennica 163 """
    if tree.species == 1:
        growth_percent = math.exp(
                5.4625
                - 0.6675 * math.log(biological_age_aggregate)
                - 0.4758 * math.log(basal_area_total)
                + 0.1173 * math.log(d13_aggregate)
                - 0.9442 * math.log(dominant_height)
                - 0.3631 * math.log(tree.breast_height_diameter)
                + 0.7762 * math.log(tree.height)
            )
    else:
        growth_percent = math.exp(
                6.9342
                - 0.8808 * math.log(biological_age_aggregate)
                - 0.4982 * math.log(basal_area_total)
                + 0.4159 * math.log(d13_aggregate)
                - 0.3865 * math.log(height_aggregate)
                - 0.6267 * math.log(tree.breast_height_diameter)
                + 0.1287 * math.log(tree.height)
            )
    return growth_percent


def yearly_height_growth_by_species(tree: ReferenceTree, biological_age_aggregate: float, d13_aggregate: float,
                                    height_aggregate: float, dominant_height: float, basal_area_total: float) -> float:
    """ Model source: Acta Forestalia Fennica 163 """
    if tree.species == 1:
        growth_percent = math.exp(
                5.4636
                - 0.9002 * math.log(biological_age_aggregate)
                + 0.5475 * math.log(d13_aggregate)
                - 1.1339 * math.log(tree.height)
            )
    else:
        growth_percent = \
        12.7402
        - 1.1786 * math.log(biological_age_aggregate)
        - 0.0937 * math.log(basal_area_total)
        - 0.1434 * math.log(d13_aggregate)
        - 0.8070 * math.log(height_aggregate)
        + 0.7563 * math.log(tree.breast_height_diameter)
        - 2.0522 * math.log(tree.height)
    return growth_percent


def grow(stand: ForestStand, **operation_parameters) -> ForestStand:
    # TODO: Source years from simulator configurations
    years = 5
    # Count ForestStand aggregate values
    basal_area_total = f_util.calculate_attribute_sum(stand.reference_trees, f_util.calculate_basal_area)
    dominant_height = f_util.solve_dominant_height(stand.reference_trees)
    # Group reference trees with same species
    tree_groups = itertools.groupby(stand.reference_trees, lambda tree: tree.species)
    # Calculate growth for each tree species
    for _, tree_group in tree_groups:
        trees = list(tree_group)
        # Count species spesific aggregate values
        d13_aggregate = f_util.calculate_basal_area_weighted_attribute_aggregate(
                trees,
                lambda tree: tree.breast_height_diameter * f_util.calculate_basal_area(tree)
            )
        height_aggregate = f_util.calculate_basal_area_weighted_attribute_aggregate(
                trees,
                lambda tree: tree.height * f_util.calculate_basal_area(tree)
            )
        biological_age_aggregate = f_util.calculate_basal_area_weighted_attribute_aggregate(
                trees,
                lambda tree: tree.biological_age * f_util.calculate_basal_area(tree)
            )
        # Solve and update growth for each tree
        for tree in trees:
            # Calculate yearly growth percents
            growth_percent_diameter = yearly_diameter_growth_by_species(
                tree,
                biological_age_aggregate,
                d13_aggregate,
                height_aggregate,
                dominant_height,
                basal_area_total)
            growth_percent_height = yearly_height_growth_by_species(
                tree,
                biological_age_aggregate,
                d13_aggregate,
                height_aggregate,
                dominant_height,
                basal_area_total)
            # Calculate the growth and update tree
            tree.breast_height_diameter = tree.breast_height_diameter * f_util.compounded_growth_factor(growth_percent_diameter, years)
            tree.height = tree.height * f_util.compounded_growth_factor(growth_percent_height, years)
    return stand


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
    'grow': grow,
    'basal_area_thinning': basal_area_thinning,
    'stem_count_thinning': stem_count_thinning,
    'continuous_growth_thinning': continuous_growth_thinning,
    'reporting': reporting,
    'print_volume': print_volume
}
