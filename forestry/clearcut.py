from forestdatamodel.model import ForestStand
from forestry.clearcutting_limits import *
from forestryfunctions import forestry_utils as futil
import enum
from forestry.cross_cutting import CrossCuttableTree
from sim.core_types import AggregatedResults, OpTuple

def _clearcut_with_output(
    stand:ForestStand,
    aggr: AggregatedResults,
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
                tag,
                aggr.current_time_point
                )
                for t in stand.reference_trees
            ]
    aggr.extend_list_result("felled_trees", trees)
    stand.reference_trees = []

    return stand, aggr

class SoilPreparationKey(enum.IntEnum):
    NONE = 0
    SCALPING = 1
    HARROWING = 2
    PATCH_MOUNDING = 3 
    DITCH_MOUNDING = 4
    INVERTING = 5
    OTHER = 6

class RegenerationKey(enum.IntEnum):
    NATURAL = 1
    SEEDED = 2
    PLANTED = 3



def clearcutting(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """checks if either stand mean age or stand basal area weighted mean 
    diameter is over limits given in separate files. 
    If yes, function clearcut is called 
    """
    stand, simulation_aggregates = input
    
    if len(stand.reference_trees)>0 and sum(x.breast_height_diameter for x in stand.reference_trees)>0:
        age_limits_path = operation_parameters.get('clearcutting_limits_ages', None)
        diameter_limits_path = operation_parameters.get('clearcutting_limits_diameters', None)
        (age_limit, diameter_limit) = get_clearcutting_limits(stand,age_limits_path, diameter_limits_path)
        age_limit_reached = futil.mean_age_stand(stand)>= age_limit
        diameter_limit_reached = futil.calculate_basal_area_weighted_attribute_sum(stand.reference_trees,
        f=lambda x: x.breast_height_diameter*futil.calculate_basal_area(x))>=diameter_limit
        if age_limit_reached or diameter_limit_reached:
            stand, aggr= _clearcut_with_output(stand,simulation_aggregates,'clearcutting')
            return (stand,aggr)
        else:
            raise UserWarning("Unable to perform clearcutting")
    else:
        raise UserWarning("Unable to perform clearcutting")


    