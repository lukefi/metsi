from forestryfunctions.naturalprocess.grow_acta import grow_diameter_and_height, grow_saplings
from forestdatamodel.model import ForestStand, ReferenceTree


def split_sapling_trees(trees: list[ReferenceTree]) -> tuple[list[ReferenceTree], list[ReferenceTree]]:
    saplings, matures = [], []
    for tree in trees:
        saplings.append(tree) if tree.sapling is True else matures.append(tree)
    return saplings, matures


def grow_acta(input: tuple[ForestStand, None], **operation_parameters) -> tuple[ForestStand, None]:
    # TODO: Source years from simulator configurations
    stand, _ = input
    if len(stand.reference_trees) == 0:
        return input
    saplings, matures = split_sapling_trees(stand.reference_trees)
    if len(saplings)>0:
        grow_saplings(saplings)
    if len(matures)>0:
        grow_diameter_and_height(matures)
    return stand, None
