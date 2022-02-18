import typing
from typing import Any
from sim.core_types import OperationPayload
from sim.util import get_or_default, dict_value


def do_nothing(data: Any) -> Any:
    print("Did nothing")
    return data


def prepared_operation(operation_entrypoint: typing.Callable, **operation_parameters):
    """prepares an opertion entrypoint function with configuration parameters"""
    return lambda state: operation_entrypoint(state, **operation_parameters)


def prepared_processor(operation_tag, processor_lookup, **operation_parameters: dict):
    """prepares a processor function with an operation entrypoint"""
    operation = prepared_operation(resolve_operation(operation_tag, processor_lookup), **operation_parameters)
    return lambda payload: processor(payload, operation)


def processor(payload: OperationPayload, operation: typing.Callable):
    """Managed run conditions and history of a simulator operation. Evaluates the operation."""

    # TODO: run_history for operation
    # TODO: run conditions for operation (is below minimum interval)
    newstate = operation(payload.simulation_state)
    newpayload = OperationPayload(
        simulation_state=newstate
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
