from forestryfunctions.naturalprocess.grow_motti import MottiGrowthPredictor
from forestdatamodel.model import ForestStand
from forestry.utils.growth import update_stand_growth


def grow_motti(input: tuple[ForestStand, None], **operation_parameters) -> tuple[ForestStand, None]:
    step = operation_parameters.get('step', 5)
    stand, _ = input
    growth = MottiGrowthPredictor(stand).evolve()
    # Motti returns deltas.
    diameters = list(map(lambda x: x[0].breast_height_diameter + x[1], zip(stand.reference_trees, growth.trees_id)))
    heights = list(map(lambda x: x[0].height + x[1], zip(stand.reference_trees, growth.trees_ih)))
    stems = list(map(lambda x: x[0].stems_per_ha + x[1], zip(stand.reference_trees, growth.trees_if)))
    update_stand_growth(stand, diameters, heights, stems, step)
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
