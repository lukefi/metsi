from collections import OrderedDict
from typing import Tuple
from forestdatamodel.model import ForestStand, ReferenceTree
from forestry.clearcutting_limits import *
from forestry.aggregate_utils import store_operation_aggregate, get_operation_aggregates, get_latest_operation_aggregate
from forestdatamodel.enums.internal import TreeSpecies
import enum
from forestry import cross_cutting as cross_cut


#forestry_function_library/harvest:
def clearcut(stand:ForestStand) -> Tuple[ForestStand, dict]:
    """Clears the stand's reference tree list
    :returns: clearcut stand and removed reference trees as dict 
    """
    #initialises the thinning_output dictionary where stems_removed_per_ha is aggregated to during the thinning operation
    clearcut_output = {
        rt.identifier: 
            {
                'stems_removed_per_ha': 0.0,
                'species': rt.species,
                'breast_height_diameter': rt.breast_height_diameter,
                'height': rt.height,
                'stems_per_ha': rt.stems_per_ha,
                'stand_area': stand.area,
            } 
            for rt in stand.reference_trees
        }

    for i,rt in enumerate(stand.reference_trees):
            clearcut_output[rt.identifier]["stems_removed_per_ha"] = rt.stems_per_ha

    stand.reference_trees = []
    new_aggregate = {'clearcut_output': clearcut_output}
    return (stand, new_aggregate)

class SoilPreparationKey(enum.IntEnum):
    SCALPING = 1
    MOUNDING = 2
    HARROWING = 3
    OTHER = 4

def plant(stand: ForestStand, regen_species: TreeSpecies, rt_count: int,rt_stems: int, soil_preparation: SoilPreparationKey) -> Tuple[ForestStand, dict]:
    """Adds 10 (+1 aspen) reference trees to stand
    this planting function is called after clearcutting so that the simulation doesn't
    stop due to errors after clearcut.
    Not at all realistic: planted trees have height = 0.3m and although
    the trees don't yet reach breast height the tree's have breast height
    diameter of 1 cm and the funtion also adds one mature aspen /ha to the stand.
    :returns: stand after regeneration and regeneration instructions used by the function
    """
    for i in range(rt_count):
        tree = ReferenceTree(identifier=str(i),stems_per_ha=rt_stems,species=regen_species,breast_height_diameter=1,biological_age=2, height=0.3,sapling=True)
        stand.reference_trees.append(tree)
    i = rt_count +1 
    stand.reference_trees.append(ReferenceTree(identifier=str(i),species=TreeSpecies.ASPEN,stems_per_ha=1,breast_height_diameter=20,height=20,biological_age=25))
    regeneration_description = {
        'soil preparation': soil_preparation,
        'species':regen_species,
        'stems_per_ha': rt_count*rt_stems
        }
    return (stand, regeneration_description)

def clearcutting(input: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    """checks if either stand mean age or stand basal area weighted mean 
    diameter is over limits given in separate files. 
    If yes, function clearcut is called 
    """
    stand, simulation_aggregates = input
    
    if len(stand.reference_trees)>0:
        age_limits = operation_parameters.get('clearcutting_limits_ages', None)
        diameter_limits = operation_parameters.get('clearcutting_limits_diameters', None)
        instructions = operation_parameters.get('clearcutting_instructions', None)
        (age_limit, diameter_limit) = get_clearcutting_limits(stand,age_limits, diameter_limits)
        regen = get_clearcutting_instructions(stand,instructions)
        age_limit_reached = mean_age_stand(stand)>= age_limit
        diameter_limit_reached = futil.calculate_basal_area_weighted_attribute_sum(stand.reference_trees,
        f=lambda x: x.breast_height_diameter*futil.calculate_basal_area(x))>=diameter_limit
    
        if age_limit_reached or diameter_limit_reached:
            stand, new_aggregate = clearcut(stand)
            stand, regeneration_description = plant(stand, 
            regen_species = regen['species'], rt_count = 10, rt_stems= regen['stems/ha']/10, 
            soil_preparation=regen['soil preparation'])
        else:
            raise UserWarning("Unable to perform clearcutting")
    else:
        raise UserWarning("Unable to perform clearcutting")
    return stand, store_operation_aggregate(simulation_aggregates,new_aggregate,'clearcutting')

def report_overall_removal_clearcut_assortments(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    """For testing, does not really make sense to report clearcutting volumes separately,
    """
    stand, simulation_aggregates = payload
    operation_tags = operation_parameters['harvest_method']
    report_removal_collection = {}
    harvest_aggregates = get_latest_operation_aggregate(simulation_aggregates, 'clearcutting')
    if harvest_aggregates is None:
        new_aggregate = 0.0
    else:
        trees = harvest_aggregates['clearcut_output']
        volumes, values = cross_cut.cross_cut_thinning_output(trees)
        new_aggregate = round(sum(map(sum, volumes))*1000/stand.area,0)
    report_removal_collection['clearcutting'] = new_aggregate

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, report_removal_collection, 'report_overall_removal_clearcut_assortments')

    return stand, new_simulation_aggregates



