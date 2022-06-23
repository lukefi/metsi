from typing import Any, List, Tuple
from forestdatamodel.model import ReferenceTree, ForestStand
from forestdatamodel.enums.internal import TreeSpecies
import rpy2.robjects as robjects
from forestry.r_utils import convert_r_named_list_to_py_dict

_cross_cut_species_mapper = {
    TreeSpecies.PINE: "pine",
    TreeSpecies.SPRUCE: "spruce",
    TreeSpecies.CURLY_BIRCH: "birch",
    TreeSpecies.DOWNY_BIRCH: "birch",
    TreeSpecies.SILVER_BIRCH: "birch"
}

def _cross_cut(tree: ReferenceTree, r: robjects.R ) -> dict:
    species = _cross_cut_species_mapper.get(tree.species, "birch") #birch is used as the default species in cross cutting
    result = r["cross_cut"](
        species,
        round(tree.breast_height_diameter), #TODO: find a better way than rounding. cross_cut function currently doesn't handle floats well..
        round(tree.height)
    )
    
    result = convert_r_named_list_to_py_dict(result)
    return (result["volumes"], result["values"])


def cross_cut_stand(stand: ForestStand) -> tuple[List[float], List[float]]:
    """
    Calculates the total volume and value of cross cutting in the :stand:. 
    """
    r = robjects.R() #initialise the singleton instance here so that the main function can be sourced only once and not for each tree
    r.source("r/cross_cutting/cross_cutting_main.R")

    # these buckets are of size (m, n) where:
        # m is the number of unique timber grades (puutavaralaji) and 
        # n is the count of reference trees in the stand.
    # it's left to the caller to generate aggregates from these.
    volumes_bucket = []
    values_bucket = []

    for tree in stand.reference_trees:
        volumes, values = _cross_cut(tree, r)

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
