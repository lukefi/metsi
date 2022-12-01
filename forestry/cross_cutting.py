from sim.core_types import OpTuple
from forestdatamodel.model import ForestStand
from forestryfunctions.cross_cutting.model import cross_cuttable_trees_from_stand
from forestry.utils import get_timber_price_table
from forestryfunctions.cross_cutting import cross_cutting

def cross_cut_felled_trees(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Calculates cross cutting volumes and values for CrossCuttableTrees that haven't yet been cross cut.
    :returns: the same payload as was given as input, but with cross cutting results stored in the simulation_aggregates.
    """
    stand, simulation_aggregates = payload
    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])

    results = []

    felled_trees = simulation_aggregates.get_list_result("felled_trees")
    felled_trees.sort(key=lambda x: x.cross_cut_done) # elements with `cross_cut_done = False` will be first
        
    for tree in felled_trees:
        if tree.cross_cut_done == True:
            break
        res = cross_cutting.cross_cut_tree(tree, stand.area, timber_price_table)
        results.extend(res)
        tree.cross_cut_done = True

    simulation_aggregates.extend_list_result("cross_cutting", results)
    return payload


def cross_cut_standing_trees(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Cross cuts the `payload`'s stand at its current state. Does not modify the state, only calculates and stores the result of cross cutting.
    The results are stored in simulation_aggregates.
    """
    stand, simulation_aggregates = payload
    tag = "standing_trees"
    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
    cross_cuttable_trees = cross_cuttable_trees_from_stand(stand, tag, simulation_aggregates.current_time_point)

    results = []
    for tree in cross_cuttable_trees:
        res = cross_cutting.cross_cut_tree(tree, stand.area, timber_price_table)
        results.extend(res)

    simulation_aggregates.extend_list_result("cross_cutting", results)

    return payload

