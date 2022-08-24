from typing import Tuple, Any, Optional
from collections import OrderedDict

def _get_operation_results(simulation_aggregates):
    return simulation_aggregates['operation_results']

def get_operation_aggregates(simulation_aggregates: dict, operation_tag: str, return_type=None) -> Optional[OrderedDict]:
    operation_results = _get_operation_results(simulation_aggregates)
    return operation_results.get(operation_tag, return_type)

def get_latest_operation_aggregate(simulation_aggregates: dict, operation_tag: str) -> Any:
    operation_aggregates = get_operation_aggregates(simulation_aggregates, operation_tag)
    if operation_aggregates is not None:
        return list(operation_aggregates.values())[-1]
    else:
        return None

def store_operation_aggregate(simulation_aggregates: dict, new_aggregate: Any, operation_tag: str) -> dict:
    time_point = simulation_aggregates['current_time_point']
    operation_results = _get_operation_results(simulation_aggregates)
    operation_aggregates = get_operation_aggregates(simulation_aggregates, operation_tag, return_type=OrderedDict())
    operation_aggregates[time_point] = new_aggregate
    operation_results[operation_tag] = operation_aggregates
    return simulation_aggregates

def store_post_processing_aggregate(simulation_aggregates: dict, new_aggregate: Any, operation_tag: str) -> dict:
    """stores :new_aggregate: under an :operation_tag: that is on the top level in the :simulation_aggregates: dict."""
    current_results = simulation_aggregates.get(operation_tag, {})
    current_results.update(new_aggregate)
    simulation_aggregates[operation_tag] = current_results
    return simulation_aggregates




