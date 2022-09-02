from typing import Tuple
from forestryfunctions.naturalprocess.grow_motti import MottiGrowthPredictor
from forestdatamodel.model import ForestStand


def grow_motti(input: Tuple[ForestStand, None], **operation_parameters) -> Tuple[ForestStand, None]:
    stand, _ = input
    growth = MottiGrowthPredictor(stand).evolve()
    for i, t in enumerate(stand.reference_trees):
        t.stems_per_ha += growth.trees_if[i]
        t.breast_height_diameter += growth.trees_id[i]
        t.height += growth.trees_ih[i]
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
