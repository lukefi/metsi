from forestry.ForestDataModels import ForestStand


def grow(stand: ForestStand, **operation_parameters) -> ForestStand:
    """This function is a no-op example stub"""
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
    elif level is 1:
        print("Stand {} appears to be quite green!".format(stand.identifier))
    return stand


operation_lookup = {
    'grow': grow,
    'basal_area_thinning': basal_area_thinning,
    'stem_count_thinning': stem_count_thinning,
    'continuous_growth_thinning': continuous_growth_thinning,
    'reporting': reporting
}
