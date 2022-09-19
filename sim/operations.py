import typing
from typing import Any, List, Optional, Tuple
from sim.core_types import OperationPayload
from sim.util import get_or_default, dict_value


def _get_operation_last_run(operation_history: List[Tuple[int, str]], operation_tag: str) -> Optional[int]:
    return next((t for t, o in reversed(operation_history) if o == operation_tag), None)


def do_nothing(data: Any, **kwargs) -> Any:
    return data


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
    current_operation_last_run_time_point = _get_operation_last_run(payload.operation_history, operation_tag)
    if operation_run_constraints is not None:
        check_operation_is_eligible_to_run(operation_tag, time_point, operation_run_constraints, current_operation_last_run_time_point)

    payload.aggregated_results['current_time_point'] = time_point
    payload.aggregated_results['current_operation_tag'] = operation_tag
    try:
        new_state, new_aggregated_results = operation((payload.simulation_state, payload.aggregated_results))
    except UserWarning as e:
        raise UserWarning("Unable to perform operation {}, at time point {}; reason: {}".format(operation_tag, time_point, e))

    payload.operation_history.append((time_point, operation_tag))

    newpayload = OperationPayload(
        simulation_state=new_state,
        aggregated_results=payload.aggregated_results if new_aggregated_results is None else new_aggregated_results,
        operation_history=payload.operation_history
    )
    return newpayload

def check_operation_is_eligible_to_run(operation_tag, time_point, operation_run_constraints, operation_last_run_time_point):
    minimum_time_interval = operation_run_constraints.get('minimum_time_interval')
    if operation_last_run_time_point is not None and minimum_time_interval > (time_point - operation_last_run_time_point):
        raise UserWarning("{} aborted - last run at {}, time now {}, minimum time interval {}"
                              .format(operation_tag, operation_last_run_time_point, time_point, minimum_time_interval))


def resolve_operation(tag: str, external_operation_lookup: dict) -> typing.Callable:
    operation = get_or_default(
        dict_value(external_operation_lookup, tag),
        dict_value(internal_operation_lookup, tag))
    if operation is None:
        raise Exception("Operation " + tag + " not available")
    else:
        return operation


internal_operation_lookup = {
    'do_nothing': do_nothing
}
