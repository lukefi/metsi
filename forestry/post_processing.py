from collections import defaultdict
from sim.core_types import OpTuple
from forestdatamodel.model import ForestStand
from forestryfunctions.cross_cutting import cross_cutting
from forestryfunctions.cross_cutting.model import CrossCutAggregate, ThinningOutput

def cross_cut_thinning_output(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    This operation can be used in post-processing to calculate cross cutting volumes and values for thinning output that was produced during a simulator run.
    This is an alternative to performing cross cutting during the simulator runtime.
    :returns: the same payload as was given as input, but with the cross cutting results stored in the simulation_aggregates. 
    """
    stand, simulation_aggregates = payload
    thinning_aggregates = defaultdict(dict)
    for tag, res in simulation_aggregates.operation_results.items():
        for tp, aggr in res.items():
            if not isinstance(aggr, ThinningOutput):
                continue
            volumes, values = cross_cutting.cross_cut_thinning_output(aggr, stand_area=stand.area)
            total_volume, total_value = cross_cutting.calculate_cross_cut_aggregates(volumes, values)
            thinning_aggregates[tag][tp] = CrossCutAggregate(total_volume, total_value)
    simulation_aggregates.get("thinning_stats").update(thinning_aggregates)
    return payload


pp_operation_lookup = {
    "cross_cut_thinning_output": cross_cut_thinning_output
}