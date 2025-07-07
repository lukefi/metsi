from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.forestry_operations.clearcutting_limits import get_clearcutting_limits
from lukefi.metsi.forestry import forestry_utils as futil
from lukefi.metsi.domain.collected_types import CrossCuttableTree
from lukefi.metsi.sim.core_types import CollectedData, OpTuple


def _clearcut_with_output(
        stand: ForestStand,
        collected_data: CollectedData,
        tag: str) -> OpTuple[ForestStand]:
    """Clears the stand's reference tree list
    :returns: clearcut stand and removed trees as CrosCuttableTrees
    """
    trees = [
        CrossCuttableTree(
            t.stems_per_ha,
            t.species,
            t.breast_height_diameter,
            t.height,
            'harvested',
            tag,
            collected_data.current_time_point
        )
        for t in stand.reference_trees
    ]
    collected_data.extend_list_result("felled_trees", trees)
    stand.reference_trees = []

    return stand, collected_data


def clearcutting(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    """checks if either stand mean age or stand basal area weighted mean
    diameter is over limits given in separate files.
    If yes, function clearcut is called
    """
    stand, collected_data = input_

    if len(stand.reference_trees) > 0 and sum(x.breast_height_diameter for x in stand.reference_trees) > 0:
        age_limits_path = operation_parameters.get('clearcutting_limits_ages', None)
        diameter_limits_path = operation_parameters.get('clearcutting_limits_diameters', None)

        (age_limit, diameter_limit) = get_clearcutting_limits(stand, age_limits_path, diameter_limits_path)
        age_limit_reached = age_limit <= futil.mean_age_stand(stand)
        diameter_limit_reached = diameter_limit <= futil.calculate_basal_area_weighted_attribute_sum(
            stand.reference_trees,
            f=lambda x: x.breast_height_diameter * futil.calculate_basal_area(x))

        if age_limit_reached or diameter_limit_reached:
            stand, collected_data = _clearcut_with_output(stand, collected_data, 'clearcutting')
            return (stand, collected_data)
        raise UserWarning("Unable to perform clearcutting")
    raise UserWarning("Unable to perform clearcutting")
