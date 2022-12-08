from forestryfunctions.naturalprocess.grow_motti import MottiGrowthPredictor
from forestdatamodel.model import ForestStand


def grow_motti(input: tuple[ForestStand, None], **operation_parameters) -> tuple[ForestStand, None]:
    stand, _ = input
    growth = MottiGrowthPredictor(stand).evolve()
    for i, t in enumerate(stand.reference_trees):
        height_before_growth = t.height
        t.stems_per_ha += growth.trees_if[i]
        t.breast_height_diameter += growth.trees_id[i]
        t.height += growth.trees_ih[i]
        t.biological_age += 5
        if height_before_growth < 1.3 <= t.height:
            t.breast_height_age = t.biological_age
        if t.height >= 1.3 and t.sapling:
            t.sapling = False
    stand.year += 5
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
