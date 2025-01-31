
from lukefi.metsi.data.model import ReferenceTree
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.conversion.internal2mela import mela_stand


def _recreate_stand_indices(stands: StandList) -> StandList:
    for idx, stand in enumerate(stands):
        stand.set_identifiers(idx + 1)
    return stands


def _recreate_tree_indices(trees: list[ReferenceTree]) -> list[ReferenceTree]:
    for idx, tree in enumerate(trees):
        tree.tree_number = idx + 1
    return trees


def prepare_rst_output(stands: StandList, **operation_params) -> StandList:
    """Recreate forest stands for output:
        1) filtering out non-living reference trees
        2) recreating indices for reference trees
        3) filtering out non-forestland stands and empty auxiliary stands
        4) recreating indices for stands"""
    for stand in stands:
        stand.reference_trees = [t for t in stand.reference_trees if t.is_living()]
        stand.reference_trees = _recreate_tree_indices(stand.reference_trees)
    stands = [s for s in stands if (
        s.is_forest_land()
        and (not s.is_auxiliary() or s.has_trees() or s.has_strata())
    )]
    stands = _recreate_stand_indices(stands)
    return stands


def classify_values_to(stands: StandList, **operation_params) -> StandList:
    """ Give format as parameter """
    format = operation_params.get('format', None)
    if format == 'rst' or format == 'rsts':
        f = lambda s: mela_stand(s)
    return [ f(stand) for stand in stands ]


operation_lookup = {
    'prepare_rst_output': prepare_rst_output,
    'classify_values_to': classify_values_to
}

