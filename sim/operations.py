from functools import cache
import typing
from copy import deepcopy
from typing import Any, Optional, Tuple, TypeVar
from forestry.aggregate_utils import store_operation_aggregate
from sim.collectives import collect_all, autocollective, getvarfn
from sim.core_types import OperationPayload
from sim.util import get_or_default, dict_value


def do_nothing(data: Any, **kwargs) -> Any:
    return data


T = TypeVar("T")
def report_collectives(input: Tuple[T, dict], /, **collectives: str) -> Tuple[T, dict]:
    state, aggr = input
    getvar = cache(getvarfn(lambda name: autocollective(getattr(state, name)), state=state, aggr=aggr))
    result = collect_all(collectives, getvar=getvar)
    return state, store_operation_aggregate(aggr, result, 'report_collectives')


def prepared_operation(operation_entrypoint: typing.Callable, **operation_parameters):
    """prepares an opertion entrypoint function with configuration parameters"""
    return lambda state: operation_entrypoint(state, **operation_parameters)


def prepared_processor(operation_tag, processor_lookup, time_point: int, operation_run_constraints: dict,
                       **operation_parameters: dict):
    """prepares a processor function with an operation entrypoint"""
    operation = prepared_operation(resolve_operation(operation_tag, processor_lookup), **operation_parameters)
    return lambda payload: processor(payload, operation, operation_tag, time_point, operation_run_constraints)


def processor(payload: OperationPayload, operation: typing.Callable, operation_tag, time_point: int,
              operation_run_constraints: Optional[dict]):
    """Managed run conditions and history of a simulator operation. Evaluates the operation."""
    run_history = deepcopy(payload.run_history)
    operation_run_history = get_or_default(run_history.get(operation_tag), {})
    if operation_run_constraints is not None:
        # check operation constrains
        last_run_time_point = operation_run_history.get('last_run_time_point')
        minimum_time_interval = operation_run_constraints.get('minimum_time_interval')
        if last_run_time_point is not None and minimum_time_interval > (time_point - last_run_time_point):
            raise UserWarning("{} aborted - last run at {}, time now {}, minimum time interval {}"
                              .format(operation_tag, last_run_time_point, time_point, minimum_time_interval))

    payload.aggregated_results['current_time_point'] = time_point
    payload.aggregated_results['current_operation_tag'] = operation_tag
    try:
        new_state, new_aggregated_results = operation((payload.simulation_state, payload.aggregated_results))
    except UserWarning as e:
        raise UserWarning("Unable to perform operation {}, at time point {}; reason: {}".format(operation_tag, time_point, e))

    new_operation_run_history = {}
    new_operation_run_history['last_run_time_point'] = time_point
    run_history[operation_tag] = new_operation_run_history
    newpayload = OperationPayload(
        simulation_state=new_state,
        run_history=run_history,
        aggregated_results=payload.aggregated_results if new_aggregated_results is None else new_aggregated_results
    )
    return newpayload


def resolve_operation(tag: str, external_operation_lookup: dict) -> typing.Callable:
    operation = get_or_default(
        dict_value(external_operation_lookup, tag),
        dict_value(internal_operation_lookup, tag))
    if operation is None:
        raise Exception("Operation " + tag + " not available")
    else:
        return operation


internal_operation_lookup = {
    'do_nothing': do_nothing,
    'report_collectives': report_collectives
}
