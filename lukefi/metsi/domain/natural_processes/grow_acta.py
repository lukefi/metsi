from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.domain.natural_processes.util import update_stand_growth
from lukefi.metsi.forestry.naturalprocess.grow_acta import grow_diameter_and_height
from lukefi.metsi.sim.collected_data import OpTuple


def split_sapling_trees(trees: list[ReferenceTree]) -> tuple[list[ReferenceTree], list[ReferenceTree]]:
    saplings, matures = [], []
    for tree in trees:
        if tree.sapling:
            saplings.append(tree)
        else:
            matures.append(tree)
    return saplings, matures


def grow_acta(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    step = operation_parameters.get('step', 5)
    stand, collected_data = input_
    if stand.reference_trees.size == 0:
        return input_
    diameters, heights = grow_diameter_and_height(stand.reference_trees, step)
    stems = stand.reference_trees.stems_per_ha
    update_stand_growth(stand, diameters, heights, stems, step)
    return stand, collected_data
