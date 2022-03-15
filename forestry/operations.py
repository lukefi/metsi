import math
import itertools
import forestry.forestry_utils as f_util
from forestry.ForestDataModels import ForestStand, ReferenceTree

def grow(stand: ForestStand, **operation_parameters) -> ForestStand:
    """ Acta Forestalia Fennica 163 """
    print("Grow operation for stand " + str(stand.identifier))
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
                lambda tree: tree.__getattribute__('breast_height_diameter') * f_util.calculate_basal_area(tree)
            )
        height_aggregate = f_util.calculate_basal_area_weighted_attribute_aggregate(
                trees,
                lambda tree: tree.__getattribute__('height') * f_util.calculate_basal_area(tree)
            )
        biological_age_aggregate = f_util.calculate_basal_area_weighted_attribute_aggregate(
                trees,
                lambda tree: tree.__getattribute__('biological_age') * f_util.calculate_basal_area(tree)
            )
        # Solve growth for each tree with same species
        for tree in trees:
            # Calculate with the actual models
            if tree.species == 1:
                growth_percent_diameter = math.exp(5.4625-0.6675*math.log(biological_age_aggregate)-0.4758*math.log(basal_area_total)+0.1173*math.log(d13_aggregate)-0.9442*math.log(dominant_height)-0.3631*math.log(tree.breast_height_diameter)+0.7762*math.log(tree.height))
                growth_percent_height = math.exp(5.4636-0.9002*math.log(biological_age_aggregate)+0.5475*math.log(d13_aggregate)-1.1339*math.log(tree.height))
            else:
                growth_percent_diameter = math.exp(6.9342 - 0.8808*math.log(biological_age_aggregate)-0.4982*math.log(basal_area_total)+0.4159*math.log(d13_aggregate)-0.3865*math.log(height_aggregate)-0.6267*math.log(tree.breast_height_diameter)+0.1287*math.log(tree.height))
                growth_percent_height = 12.7402-1.1786*math.log(biological_age_aggregate)-0.0937*math.log(basal_area_total)-0.1434*math.log(d13_aggregate)-0.8070*math.log(height_aggregate)+0.7563*math.log(tree.breast_height_diameter)-2.0522*math.log(tree.height)
            # Calculate the growth and update tree
            tree.breast_height_diameter = tree.breast_height_diameter * f_util.compounded_growth_factor(growth_percent_diameter, years)
            tree.height = tree.height * f_util.compounded_growth_factor(growth_percent_height, years)
    return stand


def basal_area_thinning(stand: ForestStand, **operation_parameters) -> ForestStand:
    print("Attempting to basal area thin stand " + stand.identifier + " but don't know what to do :(")
    return stand


def stem_count_thinning(stand: ForestStand, **operation_parameters) -> ForestStand:
    print("Attempting to stem count thin stand " + stand.identifier + " but don't know what to do :(")
    return stand


def continuous_growth_thinning(stand: ForestStand, **operation_parameters) -> ForestStand:
    print("Attempting to continuous growth thin stand " + stand.identifier + " but don't know what to do :(")
    return stand


def reporting(stand: ForestStand, **operation_parameters) -> ForestStand:
    level = operation_parameters.get('level')
    if level is None:
        print(stand.identifier)
    elif level is 1:
        print("Stand " + stand.identifier + " appears to be quite green!")
    return stand


operation_lookup = {
    'grow': grow,
    'basal_area_thinning': basal_area_thinning,
    'stem_count_thinning': stem_count_thinning,
    'continuous_growth_thinning': continuous_growth_thinning,
    'reporting': reporting
}
