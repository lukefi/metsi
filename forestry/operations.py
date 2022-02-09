from forestry.ForestDataModels import ForestStand


def grow(stand: ForestStand, **operation_parameters) -> ForestStand:
    print("Attempting to grow stand " + stand.identifier + " but don't know what to do :(")
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
    print("Stand " + stand.identifier + " appears to be quite green!")
    return stand
