from itertools import repeat
from functools import reduce
from collections import defaultdict
from forestdatamodel.model import ForestStand
from forestry.aggregates import BiomassAggregate, CrossCutAggregate, ThinningOutput, VolumeAggregate
from forestryfunctions import forestry_utils as futil
from forestry.biomass_repola import biomasses_by_component_stand, BiomassData
from forestry.clearcut import clearcutting, report_overall_removal_clearcut_assortments
from forestry.grow_acta import grow_acta
from forestry.r_utils import lmfor_volume
from forestry.thinning import first_thinning, thinning_from_above, thinning_from_below, report_overall_removal, \
    even_thinning
from forestry.aggregate_utils import store_operation_aggregate, store_post_processing_aggregate, \
    get_latest_operation_aggregate,get_operation_aggregates
from forestry import cross_cutting
from sim.core_types import OpTuple

def compute_volume(stand: ForestStand) -> float:
    """Debug level function. Does not reflect any real usable model computation.

    Return the sum of the product of basal area and height for all reference trees in the stand"""
    return reduce(lambda acc, cur: futil.calculate_basal_area(cur) * cur.height, stand.reference_trees, 0.0)


def report_volume(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, simulation_aggregates = payload
    volume_function = compute_volume
    if operation_parameters.get('lmfor_volume'):
        volume_function = lmfor_volume
    result = volume_function(stand)
    prev = simulation_aggregates.prev('report_volume')
    simulation_aggregates.store(
        'report_volume',
        VolumeAggregate.initial(result) if prev is None
        else VolumeAggregate.from_prev(prev, result),
    )
    return payload


def cross_cut_whole_stand(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    This is the entry point for calculating cross cut (apteeraus) value and volume for a whole stand.
    """

    stand, simulation_aggregates = payload

    volumes, values = cross_cutting.cross_cut_stand(stand)

    total_volume, total_value = cross_cutting.calculate_cross_cut_aggregates(volumes, values)

    simulation_aggregates.store('report_cross_cutting', CrossCutAggregate(total_volume, total_value))

    return payload


def report_biomass(input: OpTuple[ForestStand], **operation_params) -> OpTuple[ForestStand]:
    """For the given ForestStand, this operation computes and stores the current biomass tonnage and difference to last
    calculation into the aggregate structure."""
    stand, aggregates = input
    models = operation_params.get('model_set', 1)

    # TODO: need proper functionality to find tree volumes, model_set 2 and 3 don't work properly otherwise
    volumes = list(repeat(100.0, len(stand.reference_trees)))
    # TODO: need proper functionality to find waste volumes, model_set 2 and 3 don't work properly otherwise
    wastevolumes = list(repeat(100.0, len(stand.reference_trees)))

    biomass = biomasses_by_component_stand(stand, volumes, wastevolumes, models)
    prev = aggregates.prev('report_biomass')
    aggregates.store(
        'report_biomass',
        BiomassAggregate.initial(biomass) if prev is None
        else BiomassAggregate.from_prev(prev, biomass)
    )

    return input


def cross_cut_thinning_output(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
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


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'thinning_from_below': thinning_from_below,
    'thinning_from_above': thinning_from_above,
    'first_thinning': first_thinning,
    'even_thinning': even_thinning,
    'report_biomass': report_biomass,
    'report_volume': report_volume,
    'report_overall_removal': report_overall_removal,
    'report_overall_removal_clearcut_assortments': report_overall_removal_clearcut_assortments, #Laura
    'cross_cut_whole_stand': cross_cut_whole_stand,
    'cross_cut_thinning_output': cross_cut_thinning_output,
    'clearcutting': clearcutting
}

try:
    from forestry.grow_motti import grow_motti
except ImportError:
    # just don't register it when pymotti isn't found.
    # we don't want to make pymotti a required dependency until it's public.
    pass
else:
    operation_lookup['grow_motti'] = grow_motti
