from typing import Any, Dict, List, Tuple
from forestdatamodel.model import ReferenceTree, ForestStand
from forestdatamodel.enums.internal import TreeSpecies
import rpy2.robjects as robjects
from forestry.aggregates import ThinningOutput
from forestry.r_utils import convert_r_named_list_to_py_dict

_cross_cut_species_mapper = {
    TreeSpecies.PINE: "pine",
    TreeSpecies.SPRUCE: "spruce",
    TreeSpecies.CURLY_BIRCH: "birch",
    TreeSpecies.DOWNY_BIRCH: "birch",
    TreeSpecies.SILVER_BIRCH: "birch"
}

cross_cut_loaded = False

def _get_r_with_sourced_scripts():
    global cross_cut_loaded
    r = robjects.r
    if not cross_cut_loaded:
        r.source("r/cross_cutting/cross_cutting_main.R")
        cross_cut_loaded = True
    return r


def _cross_cut(
        species: TreeSpecies,
        breast_height_diameter: float,
        height: float, 
        r: robjects.R 
        ) -> dict:

    species = _cross_cut_species_mapper.get(species, "birch") #birch is used as the default species in cross cutting
    result = r["cross_cut"](
        species,
        round(breast_height_diameter), #TODO: find a better way than rounding. cross_cut function currently doesn't handle floats well..
        round(height)
    )
    
    result = convert_r_named_list_to_py_dict(result)
    return (result["volumes"], result["values"])


def cross_cut_thinning_output(thinned_trees: ThinningOutput, stand_area: float) -> Tuple[List, List]:
    #TODO: pass in each tree to the cross_cut function and collect aggregates to be returned.
    
    r = _get_r_with_sourced_scripts()

    # these buckets are of size (m, n) where:
        # m is the number of unique timber grades (puutavaralaji) and 
        # n is the count of reference trees in the stand.
    # it's left to the caller to generate aggregates from these.

    volumes_bucket = []
    values_bucket = []

    for thinning_data in thinned_trees.removed:
        volumes, values = _cross_cut(
                            thinning_data.species,
                            thinning_data.breast_height_diameter,
                            thinning_data.height,
                            r
                            )

        #NOTE: the above 'volumes' and 'values' are calculated for a single reference tree. 
        # To report absolute (i.e. not in per hectare terms) numbers, they must be multiplied by the reference tree's stems_removed_per_ha and the stand area (in hectares)
        
        multiplier = thinning_data.stems_removed_per_ha * stand_area/1000
        volumes = [vol*multiplier for vol in volumes]
        values = [val*multiplier for val in values]

        volumes_bucket.append(volumes)
        values_bucket.append(values)
    
    return (volumes_bucket, values_bucket)



def cross_cut_stand(stand: ForestStand) -> tuple[List[float], List[float]]:
    """
    Calculates the total volume and value of cross cutting in the :stand:. 
    """
    r = _get_r_with_sourced_scripts()

    # these buckets are of size (m, n) where:
        # m is the number of unique timber grades (puutavaralaji) and 
        # n is the count of reference trees in the stand.
    # it's left to the caller to generate aggregates from these.
    volumes_bucket = []
    values_bucket = []

    for tree in stand.reference_trees:
        volumes, values = _cross_cut(
                            tree.species, 
                            tree.breast_height_diameter, 
                            tree.height, 
                            r)

        #NOTE: the above 'volumes' and 'values' are calculated for a single reference tree. To report meaningful numbers,
        # they must be multiplied by the reference tree's stem count per ha and the stand area (in hectares)
        multiplier = tree.stems_per_ha * (stand.area/1000) #area is given in square meters, thus need to convert to ha.
        volumes = [vol*multiplier for vol in volumes] 
        values = [val*multiplier for val in values]

        volumes_bucket.append(volumes)
        values_bucket.append(values)
    
    return (volumes_bucket, values_bucket)

def calculate_cross_cut_aggregates(volumes: List[List[float]], values: List[List[float]]) -> Any:
    # would math.fsum work better for floats?
    total_volume = sum(map(sum, volumes))
    total_value = sum(map(sum, values))

    return (total_volume, total_value)
