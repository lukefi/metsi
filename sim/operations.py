import typing
from copy import deepcopy
from typing import Any, Optional
from sim.core_types import OperationPayload
from sim.util import get_or_default, dict_value


def do_nothing(data: Any) -> Any:
    return data


def prepared_operation(operation_entrypoint: typing.Callable, **operation_parameters):
    """prepares an opertion entrypoint function with configuration parameters"""
    return lambda state: operation_entrypoint(state, **operation_parameters)


def prepared_processor(operation_tag, processor_lookup, time_point: int, operation_run_constrains: dict, **operation_parameters: dict):
    """prepares a processor function with an operation entrypoint"""
    operation = prepared_operation(resolve_operation(operation_tag, processor_lookup), **operation_parameters)
    return lambda payload: processor(payload, operation, operation_tag, time_point, operation_run_constrains)


def processor(payload: OperationPayload, operation: typing.Callable, operation_tag, time_point: int, operation_run_constrains: Optional[dict]):
    """Managed run conditions and history of a simulator operation. Evaluates the operation."""
    run_history = deepcopy(payload.run_history)
    operation_run_history = get_or_default(run_history.get(operation_tag), {})
    print("{}...".format(operation_tag))
    if operation_run_constrains is not None:
        # check operation constrains
        last_run_time_point = operation_run_history.get('last_run_time_point')
        minimum_time_interval = operation_run_constrains.get('minimum_time_interval')
        if last_run_time_point is not None and minimum_time_interval > (time_point - last_run_time_point):
            raise Exception("{} aborted - last run at {}, time now {}, minimum time interval {}"
                            .format(operation_tag, last_run_time_point, time_point, minimum_time_interval))
    newstate = operation(payload.simulation_state)
    new_operation_run_history = {}
    new_operation_run_history['last_run_time_point'] = time_point
    run_history[operation_tag] = new_operation_run_history
    newpayload = OperationPayload(
        simulation_state=newstate,
        run_history=run_history
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
    'do_nothing': do_nothing
}
