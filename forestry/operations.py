from itertools import repeat
from functools import reduce
from forestdatamodel.model import ForestStand
from forestry.aggregates import BiomassAggregate, VolumeAggregate
from forestryfunctions.cross_cutting.model import CrossCutAggregate
from forestryfunctions import forestry_utils as futil
from forestryfunctions.r_utils import lmfor_volume
from forestryfunctions.cross_cutting import cross_cutting
from forestry.biomass_repola import biomasses_by_component_stand
from forestry.grow_acta import grow_acta
from forestry.thinning import first_thinning, thinning_from_above, thinning_from_below, report_overall_removal, \
    even_thinning
from sim.core_types import OpTuple
from forestry.clearcut import clearcutting, clearcutting_and_planting

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
    The results are stored in simulation_aggregates.
    """

    stand, simulation_aggregates = payload

    timber_price_table = operation_parameters['timber_price_table']
    volumes, values = cross_cutting.cross_cut_stand(stand, timber_price_table)
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


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'thinning_from_below': thinning_from_below,
    'thinning_from_above': thinning_from_above,
    'first_thinning': first_thinning,
    'even_thinning': even_thinning,
    #'clearcutting': clearcutting,
    'clearcutting': clearcutting_and_planting,
    'report_biomass': report_biomass,
    'report_volume': report_volume,
    'report_overall_removal': report_overall_removal,
}

try:
    from forestry.grow_motti import grow_motti
except ImportError:
    # just don't register it when pymotti isn't found.
    # we don't want to make pymotti a required dependency until it's public.
    pass
else:
    operation_lookup['grow_motti'] = grow_motti
