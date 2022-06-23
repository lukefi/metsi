from typing import List
from forestdatamodel.model import ForestStand

def exclude_sapling_trees(stands: List[ForestStand], **operation_params) -> List[ForestStand]:
    for stand in stands:
        stand.reference_trees = list(filter(lambda t: (t if t.sapling is False else None), stand.reference_trees))
    return stands

def exclude_empty_stands(stands: List[ForestStand], **operation_params)-> List[ForestStand]:
    stands = list(filter(lambda s: (s if len(s.reference_trees) > 0 else None), stands))
    return stands

def exclude_zero_stem_trees(stands: List[ForestStand], **operation_params) -> List[ForestStand]:
    for stand in stands:
        stand.reference_trees = list(filter(lambda rt: rt.stems_per_ha > 0.0, stand.reference_trees))
    return stands

operation_lookup = {
    'exclude_sapling_trees': exclude_sapling_trees,
    'exclude_empty_stands': exclude_empty_stands,
    'exclude_zero_stem_trees': exclude_zero_stem_trees
}
