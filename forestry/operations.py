from forestryfunctions import forestry_utils as futil
from functools import reduce
from collections import OrderedDict
from typing import Tuple
from forestdatamodel.model import ForestStand
from forestry.grow_acta import grow_acta
from forestry.r_utils import lmfor_volume
from forestry.thinning import first_thinning, thinning_from_above, thinning_from_below, report_overall_removal, \
    even_thinning
from forestry.aggregate_utils import store_operation_aggregate, get_latest_operation_aggregate
# from forestry.cross_cutting import cross_cut_stand, cross_cut_thinning_output, calculate_cross_cut_aggregates
from sim.core_types import OperationPayload
import forestry.cross_cutting as cross_cutting


def compute_volume(stand: ForestStand) -> float:
    """Debug level function. Does not reflect any real usable model computation.

    Return the sum of the product of basal area and height for all reference trees in the stand"""
    return reduce(lambda acc, cur: futil.calculate_basal_area(cur) * cur.height, stand.reference_trees, 0.0)


def report_volume(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    stand, simulation_aggregates = payload
    latest_aggregate = get_latest_operation_aggregate(simulation_aggregates, 'report_volume')

    volume_function = compute_volume
    if operation_parameters.get('lmfor_volume'):
        volume_function = lmfor_volume
    result = volume_function(stand)

    if latest_aggregate is None:
        new_aggregate = {'growth_volume': 0.0, 'current_volume': result}
    else:
        new_aggregate = {
            'growth_volume': latest_aggregate['growth_volume'] + result - latest_aggregate['current_volume'],
            'current_volume': result
        }

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'report_volume')

    return stand, new_simulation_aggregates


def cross_cut_whole_stand(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    """
    This is the entry point for calculating cross cut (apteeraus) value and volume for a whole stand.
    """

    stand, simulation_aggregates = payload

    volumes, values = cross_cutting.cross_cut_stand(stand)

    total_volume, total_value = cross_cutting.calculate_cross_cut_aggregates(volumes, values)

    new_aggregate = {
        'cross_cut_volume': total_volume,
        'cross_cut_value': total_value
    }

    new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, new_aggregate, 'report_cross_cutting')

    result = (stand, new_simulation_aggregates)
    return result


def cross_cut_thinning_output(payload: Tuple[ForestStand, dict], **operation_parameters) -> Tuple[ForestStand, dict]:
    
    stand, simulation_aggregates = payload
    # proceed only if simulation_aggregates contains thinning output, although it doesn't feel ideal to rely on such a list of thinning operations as below..
    THINNING_OPERATIONS = ["thinning_from_above", "thinning_from_below", "even_thinning", "first_thinning"]
    thinning_aggregates = {}

    if not any(thinning_operation in simulation_aggregates['operation_results'] for thinning_operation in THINNING_OPERATIONS):
        return stand, simulation_aggregates
    else:
        #there's likely always only one thinning_operation in the current schedule, so this loop will only run once
        for thinning_operation in THINNING_OPERATIONS:
            if thinning_operation in simulation_aggregates['operation_results']:
                thinning_results_per_time_point = simulation_aggregates["operation_results"][thinning_operation].items()
                #is it so that a 'schedule' represents an operation in a given time point? 
                #if so, then there's only one time point per schedule, so this loop will run only once
                for time_point, thinning_results in thinning_results_per_time_point:
                    thinned_trees = thinning_results["thinning_output"]
                    volumes, values = cross_cutting.cross_cut_thinning_output(thinned_trees)

                    total_volume, total_value = cross_cutting.calculate_cross_cut_aggregates(volumes, values)
                    
                    thinning_aggregates[thinning_operation] ={
                        'cross_cut_volume': total_volume,
                        'cross_cut_value': total_value
                    }
        
        # currently I don't know whether some of these aggregates can be written into again -- this may be the case especially if operation alternatives can be branched by parameters
        # furthermore, the time_point variable in the loop doesn't always match 'current_time_point' that is used in store_operation_aggregate. Where does the difference come from?
        new_simulation_aggregates = store_operation_aggregate(simulation_aggregates, thinning_aggregates, 'report_cross_cutting')

        result = (stand, new_simulation_aggregates)
        return result


operation_lookup = {
    'grow_acta': grow_acta,
    'grow': grow_acta,  # alias for now, maybe make it parametrizable later
    'thinning_from_below': thinning_from_below,
    'thinning_from_above': thinning_from_above,
    'first_thinning': first_thinning,
    'even_thinning': even_thinning,
    'report_volume': report_volume,
    'report_overall_removal': report_overall_removal,
    'cross_cut_whole_stand': cross_cut_whole_stand,
    'cross_cut_thinning_output': cross_cut_thinning_output
}

try:
    from forestry.grow_motti import grow_motti
except ImportError:
    # just don't register it when pymotti isn't found.
    # we don't want to make pymotti a required dependency until it's public.
    pass
else:
    operation_lookup['grow_motti'] = grow_motti
