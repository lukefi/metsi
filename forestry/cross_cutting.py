from collections import defaultdict
from sim.core_types import OpTuple
from forestdatamodel.model import ForestStand
from forestryfunctions.cross_cutting.model import CrossCuttableTrees, CrossCutResults
from forestry.utils import get_timber_price_table
from forestryfunctions.cross_cutting import cross_cutting


def cross_cut_thinning_output(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Calculates cross cutting volumes and values for thinning results that haven't yet been cross cut.
    :returns: the same payload as was given as input, but with cross cutting results stored in the simulation_aggregates.
    """
    stand, simulation_aggregates = payload
    thinning_aggregates = defaultdict(dict)
    for tag, res in simulation_aggregates.operation_results.items():
        for tp, aggr in res.items():
            #cross cut only if we're dealing with a thinning aggregate, and it hasn't already been cross cut
            if isinstance(aggr, CrossCuttableTrees):
                if aggr.cross_cut_done is not True:

                    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
                    results = cross_cutting.cross_cut_trees(aggr, stand.area, timber_price_table)
                    thinning_aggregates[tag][tp] = CrossCutResults(results)
                    aggr.cross_cut_done = True

    for tag, res in thinning_aggregates.items():
        try:
            simulation_aggregates.get("thinned_trees_cross_cut")[tag].update(res)
        except KeyError:
            simulation_aggregates.get("thinned_trees_cross_cut")[tag] = res

    return payload


def cross_cut_whole_stand(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Cross cuts the `payload`'s stand at its current state. Does not modify the state, only calculates and stores the result of cross cutting.
    The results are stored in simulation_aggregates.
    """
    stand, simulation_aggregates = payload
    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
    cross_cuttable_trees = CrossCuttableTrees.from_stand(stand)
    results = cross_cutting.cross_cut_trees(cross_cuttable_trees, stand.area, timber_price_table)
    simulation_aggregates.store('standing_trees_cross_cut', results)

    return payload
