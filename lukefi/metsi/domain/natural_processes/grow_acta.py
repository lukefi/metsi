from lukefi.metsi.forestry.naturalprocess.grow_acta import grow_diameter_and_height
from lukefi.metsi.data.model import ForestStand, ReferenceTree

from lukefi.metsi.domain.natural_processes.util import update_stand_growth


def split_sapling_trees(trees: list[ReferenceTree]) -> tuple[list[ReferenceTree], list[ReferenceTree]]:
    saplings, matures = [], []
    for tree in trees:
        saplings.append(tree) if tree.sapling is True else matures.append(tree)
    return saplings, matures


def grow_acta(input_: tuple[ForestStand, None], /, **operation_parameters) -> tuple[ForestStand, None]:
    step = operation_parameters.get('step', 5)
    print("grow_acta step:", step)
    stand, _ = input_
    if len(stand.reference_trees) == 0:
        return input_
    diameters, heights = grow_diameter_and_height(stand.reference_trees, step)
    stems = list(map(lambda x: x.stems_per_ha, stand.reference_trees))
    update_stand_growth(stand, diameters, heights, stems, step)
    return stand, None
