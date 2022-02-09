import typing
from typing import Any
from forestry.operations import grow, basal_area_thinning, stem_count_thinning, continuous_growth_thinning, reporting


def do_nothing(data: Any) -> Any:
    print("Did nothing")
    return data


def prepared_operation(operation_entrypoint: typing.Callable, **operation_configuration):
    """prepares an opertion entrypoint function with configuration parameters"""
    return lambda state: operation_entrypoint(state, **operation_configuration)


def prepared_processor(operation_tag, processor_lookup, **operation_configuration: dict):
    """prepares a processor function with an operation entrypoint"""
    operation = prepared_operation(processor_lookup[operation_tag], **operation_configuration)
    return lambda payload: processor(payload, operation)


def processor(payload: dict, operation: typing.Callable):
    """Managed run conditions and history of a simulator operation. Evaluates the operation."""

    # TODO: run_history for operation
    # TODO: run conditions for operation (is below minimum interval)
    newstate = operation(payload['simulation_state'])
    newpayload = {
        'simulation_state': newstate
    }
    return newpayload


operation_lookup = {
    'do_nothing': do_nothing,
    'grow': grow,
    'basal_area_thinning': basal_area_thinning,
    'stem_count_thinning': stem_count_thinning,
    'continuous_growth_thinning': continuous_growth_thinning,
    'reporting': reporting
}
