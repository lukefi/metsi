from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.forestry.naturalprocess.grow_acta import grow_diameter_and_height, grow_diameter_and_height_vectorized
from lukefi.metsi.data.model import ForestStand, ReferenceTree

from lukefi.metsi.domain.natural_processes.util import update_stand_growth, update_stand_growth_vectorized
from lukefi.metsi.sim.core_types import OpTuple


def split_sapling_trees(trees: list[ReferenceTree]) -> tuple[list[ReferenceTree], list[ReferenceTree]]:
    saplings, matures = [], []
    for tree in trees:
        if tree.sapling:
            saplings.append(tree)
        else:
            matures.append(tree)
    return saplings, matures


def grow_acta(input_: tuple[ForestStand, None], /, **operation_parameters) -> tuple[ForestStand, None]:
    step = operation_parameters.get('step', 5)
    stand, _ = input_
    if len(stand.reference_trees) == 0:
        return input_
    diameters, heights = grow_diameter_and_height(stand.reference_trees, step)
    stems = list(map(lambda x: x.stems_per_ha, stand.reference_trees))
    update_stand_growth(stand, diameters, heights, stems, step)
    return stand, None

def grow_acta_vectorized(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    step = operation_parameters.get('step', 5)
    stand, _ = input_
    if stand.reference_trees_soa is None:
        raise MetsiException("Reference trees not vectorized")
    if stand.reference_trees_soa.size == 0:
        return input_
    diameters, heights = grow_diameter_and_height_vectorized(stand.reference_trees_soa, step)
    stems = stand.reference_trees_soa.stems_per_ha
    update_stand_growth_vectorized(stand, diameters, heights, stems, step)
    return stand, None
    