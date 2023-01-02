import numpy as np
from domain.collected_types import CrossCutResult, CrossCuttableTree
from sim.core_types import OpTuple
from lukefi.metsi.data.model import ForestStand
from domain.utils.file_io import get_timber_price_table
from lukefi.metsi.forestry.cross_cutting.cross_cutting import cross_cut
from lukefi.metsi.forestry.cross_cutting.cross_cutting_fhk import cross_cut_func
from lukefi.metsi.data.enums.internal import TreeSpecies


def cross_cuttable_trees_from_stand(stand: ForestStand, time_point: int) -> list[CrossCuttableTree]:
     return [
            CrossCuttableTree(
                tree.stems_per_ha,
                tree.species,
                tree.breast_height_diameter,
                tree.height,
                'standing',
                '',
                time_point
                )
                for tree in stand.reference_trees
            ]


def _create_cross_cut_results(
    stand_area: float,
    species: TreeSpecies,
    stems_removed_per_ha: float,
    unique_timber_grades,
    volumes: float,
    values: float,
    tree_source: str,
    operation: str,
    time_point: int
    ) -> list[CrossCutResult]:
    results = []
    for grade, volume, value in zip(unique_timber_grades, volumes, values):
        results.append(
                CrossCutResult(
                    species=species,
                    timber_grade=int(grade),
                    volume_per_ha=volume*stems_removed_per_ha,
                    value_per_ha=value*stems_removed_per_ha,
                    stand_area=stand_area,
                    source=tree_source,
                    operation=operation,
                    time_point=time_point
                )
            )
    return results


def cross_cut_tree(
    tree: CrossCuttableTree,
    stand_area: float,
    timber_price_table: np.ndarray,
    mode: str = "py"
    ) -> list[CrossCutResult]:
    """
    :param tree: The tree to cross cut
    :param stand_area: Stand area
    :param timber_price_table: Timber price table
    :param mode: implementation to use (py, lua)
    :returns: A list of CrossCutResult objects, whose length is given by the number of unique timber grades in the `timber_price_table`. In other words, the returned list contains the resulting quantities of each unique timber grade.
    """
    if mode == "lua":
        cross_cut_fn = lambda: cross_cut_func(timber_price_table)(tree.species, tree.breast_height_diameter, tree.height)
    else:
        cross_cut_fn = lambda: cross_cut(tree.species, tree.breast_height_diameter, tree.height, timber_price_table)

    unique_timber_grades, volumes, values = cross_cut_fn()

    res = _create_cross_cut_results(
                        stand_area,
                        tree.species,
                        tree.stems_per_ha,
                        unique_timber_grades,
                        volumes,
                        values,
                        tree.source,
                        tree.operation,
                        tree.time_point
                        )
    return res


def cross_cut_felled_trees(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Calculates cross cutting volumes and values for CrossCuttableTrees that haven't yet been cross cut.
    :returns: the same payload as was given as input, but with cross cutting results stored in the collected_data.
    """
    stand, collected_data = payload
    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
    impl = operation_parameters.get('implementation', 'py')

    results = []


    felled_trees = collected_data.get_list_result("felled_trees")
    felled_trees_not_cut = filter(lambda x: not x.cross_cut_done, felled_trees)

    for tree in felled_trees_not_cut:
        res = cross_cut_tree(tree, stand.area, timber_price_table, impl)
        results.extend(res)
        tree.cross_cut_done = True

    collected_data.extend_list_result("cross_cutting", results)
    return payload


def cross_cut_standing_trees(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Cross cuts the `payload`'s stand at its current state. Does not modify the state, only calculates and stores the result of cross cutting.
    The results are stored in collected_data.
    """
    stand, collected_data = payload
    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
    cross_cuttable_trees = cross_cuttable_trees_from_stand(stand, collected_data.current_time_point)
    impl = operation_parameters.get('implementation', 'py')

    results = []
    for tree in cross_cuttable_trees:
        res = cross_cut_tree(tree, stand.area, timber_price_table, impl)
        results.extend(res)

    collected_data.extend_list_result("cross_cutting", results)

    return payload

