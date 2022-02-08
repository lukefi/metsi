import typing
from math import log, e
from typing import Any, Optional

from sim.ForestDataModels import ForestStand


def grow(volume: float) -> Optional[float]:
    if volume is None:
        return None
    multiplier = 1 + 1 / log(volume, e)
    result = multiplier * volume
    print("Forest growing by factor of " + str(multiplier) + ". V = " + str(volume) + " -> " + str(multiplier * volume))
    return result


def cut(volume: float, pct: float = 100) -> Optional[float]:
    if volume is None:
        return None
    multiplier = pct / 100
    result = volume - multiplier * volume
    if can_cut(volume) is False:
        raise Exception("Can not cut " + str(pct) + " %. Tree volume " + str(result) + " is below cutting threshold.")

    print("Cutting " + str(pct) + " %. V = " + str(volume) + " -> " + str(result))
    return result


def can_cut(volume: float, threshold: float = 200) -> bool:
    return volume > threshold


def do_nothing(data: Any) -> Any:
    print("Did nothing")
    return data


def plant(volume: float, amount: int) -> Optional[float]:
    if volume is None:
        return None
    increase = amount / 100
    result = volume + increase
    print("Planting " + str(amount) + " trees. V now " + str(result))
    return result


def basal_area_thinning(X):
    print("basal area thinning")
    return X


def stem_count_thinning(X):
    print("stem count thinning")
    return X


def continuous_growth_thinning(X):
    print("continuous growth thinning")
    return X


def reporting(X):
    print('information output stub')
    return X


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
