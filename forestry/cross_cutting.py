from collections import defaultdict
from sim.core_types import AggregatedResults, OpTuple
from forestdatamodel.model import ForestStand
from forestryfunctions.cross_cutting.model import CrossCuttableTrees
from forestry.utils import get_timber_price_table
from forestryfunctions.cross_cutting import cross_cutting

def _store_cross_cutting_results(simulation_aggregates: AggregatedResults, cross_cut_result_aggregate: defaultdict) -> AggregatedResults:
    for tag, res in cross_cut_result_aggregate.items():
        try:
            simulation_aggregates.get("cross_cutting")[tag].update(res)
        except KeyError:
            simulation_aggregates.get("cross_cutting")[tag] = res


def cross_cut_felled_trees(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Calculates cross cutting volumes and values for CrossCuttableTrees that haven't yet been cross cut.
    :returns: the same payload as was given as input, but with cross cutting results stored in the simulation_aggregates.
    """
    stand, simulation_aggregates = payload
    cross_cut_result_aggregate = defaultdict(dict)
    for tag, res in simulation_aggregates.operation_results.items():
        for tp, aggr in res.items():
            #cross cut only if we're dealing with a thinning aggregate, and it hasn't already been cross cut
            if isinstance(aggr, CrossCuttableTrees):
                if aggr.cross_cut_done is not True:

                    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
                    results = cross_cutting.cross_cut_trees(aggr, stand.area, timber_price_table)
                    cross_cut_result_aggregate[tag][tp] = results
                    aggr.cross_cut_done = True

    _store_cross_cutting_results(simulation_aggregates, cross_cut_result_aggregate)

    return payload


def cross_cut_whole_stand(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Cross cuts the `payload`'s stand at its current state. Does not modify the state, only calculates and stores the result of cross cutting.
    The results are stored in simulation_aggregates.
    """
    stand, simulation_aggregates = payload
    cross_cut_result_aggregate = defaultdict(dict)

    timber_price_table = get_timber_price_table(operation_parameters['timber_price_table'])
    cross_cuttable_trees = CrossCuttableTrees.from_stand(stand)
    results = cross_cutting.cross_cut_trees(cross_cuttable_trees, stand.area, timber_price_table)
    cross_cut_result_aggregate["standing_trees"][simulation_aggregates.current_time_point] = results

    _store_cross_cutting_results(simulation_aggregates, cross_cut_result_aggregate)

    return payload

