from typing import Tuple
from forestdatamodel.model import ForestStand, ReferenceTree
from forestryfunctions.cross_cutting.model import  CrossCuttableTrees,CrossCuttableTree
from forestry.clearcutting_limits import *
from forestryfunctions import forestry_utils as futil
from forestdatamodel.enums.internal import TreeSpecies
import enum
from sim.core_types import AggregatedResults, OpTuple

def clearcut_with_output(
    stand:ForestStand,
    aggr: AggregatedResults,
    tag: str) -> OpTuple[ForestStand]:
    """Clears the stand's reference tree list
    :returns: clearcut stand and removed trees as CrosCuttableTrees
    """
    #initialises the thinning_output dictionary where stems_removed_per_ha is aggregated to during the thinning operation
    aggr.store(
        tag,
        CrossCuttableTrees([
            CrossCuttableTree(t.stems_per_ha, t.species, t.breast_height_diameter, t.height)
                for t in stand.reference_trees
        ])
    ) 
    stand.reference_trees = []
    #pois ffl ja lisäys tähän
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


def plant(stand: ForestStand, aggr: AggregatedResults, tag: str,regen_species: TreeSpecies, rt_count: int,rt_stems: int, soil_preparation: SoilPreparationKey) -> OpTuple[ForestStand]:
    """Adds 10 reference trees to stand
    this planting function is called after clearcutting so that the simulation doesn't
    stop due to errors after clearcut.
    """
    for i in range(rt_count):
        tree_id = stand.identifier + f"-{i}-tree"
        tree = ReferenceTree(identifier=tree_id,stems_per_ha=rt_stems/rt_count,species=regen_species,breast_height_diameter=0,biological_age=1, height=0.3,sapling=True)
        stand.reference_trees.append(tree)
    
    regeneration_description = {
        'regeneration': RegenerationKey.PLANTED,
        'soil preparation': soil_preparation,
        'species':regen_species,
        'stems_per_ha': rt_count*rt_stems
    }
    aggr.store(
        tag, regeneration_description
    ) 
    return (stand, aggr)

def clearcutting(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """checks if either stand mean age or stand basal area weighted mean 
    diameter is over limits given in separate files. 
    If yes, function clearcut is called 
    """
    stand, simulation_aggregates = input
    
    if len(stand.reference_trees)>0:
        age_limits_path = operation_parameters.get('clearcutting_limits_ages', None)
        diameter_limits_path = operation_parameters.get('clearcutting_limits_diameters', None)
        (age_limit, diameter_limit) = get_clearcutting_limits(stand,age_limits_path, diameter_limits_path)
        age_limit_reached = futil.mean_age_stand(stand)>= age_limit
        diameter_limit_reached = futil.calculate_basal_area_weighted_attribute_sum(stand.reference_trees,
        f=lambda x: x.breast_height_diameter*futil.calculate_basal_area(x))>=diameter_limit
        if age_limit_reached or diameter_limit_reached:
            stand, output= clearcut_with_output(stand,simulation_aggregates,'clearcutting')
            return (stand,output)
        else:
            raise UserWarning("Unable to perform clearcutting")
    else:
        raise UserWarning("Unable to perform clearcutting")

def clearcutting_and_planting(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """checks if either stand mean age or stand basal area weighted mean 
    diameter is over limits given in separate files. 
    If yes, function clearcut is called 
    """
    stand, simulation_aggregates = input
    
    if len(stand.reference_trees)>0:
        age_limits_path = operation_parameters.get('clearcutting_limits_ages', None)
        diameter_limits_path = operation_parameters.get('clearcutting_limits_diameters', None)
        instructions_path = operation_parameters.get('clearcutting_instructions', None)
        (age_limit, diameter_limit) = get_clearcutting_limits(stand,age_limits_path, diameter_limits_path)
        regen = get_clearcutting_instructions(stand,instructions_path)
        age_limit_reached = futil.mean_age_stand(stand)>= age_limit
        diameter_limit_reached = futil.calculate_basal_area_weighted_attribute_sum(stand.reference_trees,
        f=lambda x: x.breast_height_diameter*futil.calculate_basal_area(x))>=diameter_limit
    
        if age_limit_reached or diameter_limit_reached:
            stand, output = clearcut_with_output(stand,simulation_aggregates,'clearcutting')
            stand, output_planting = plant(stand,output,"regeneration",regen['species'],10,regen['stems/ha'],regen['soil preparation'])
            return (stand,output_planting)
        else:
            raise UserWarning("Unable to perform clearcutting")
    else:
        raise UserWarning("Unable to perform clearcutting")
 