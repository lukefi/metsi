from math import log
from typing import Any, Optional


def grow(volume: float) -> Optional[float]:
    if volume is None:
        return None
    multiplier = 1 + 1 / log(volume, 10)
    result = multiplier * volume
    print("Forest growing by factor of " + str(multiplier) + ". V = " + str(volume) + " -> " + str(multiplier * volume))
    return result


def cut(volume: float, pct: float = 100) -> Optional[float]:
    if volume is None:
        return None
    multiplier = pct / 100
    result = volume - multiplier * volume
    minimum_remaining = 15000
    if can_cut(result, minimum_remaining) is False:
        raise Exception("Tree volume " + str(volume) + " is below cutting threshold " + str(minimum_remaining) + ".")
    print("Cutting " + str(pct) + " %. V = " + str(volume) + " -> " + str(result))
    return result


def can_cut(volume: float, threshold: float = 15000) -> bool:
    return volume > threshold


def do_nothing(data: Any) -> Any:
    return data


def plant(volume: float, amount: int) -> Optional[float]:
    if volume is None:
        return None
    increase = amount / 100
    result = volume + increase
    print("Planting " + str(amount) + " trees. V now " + str(result))
    return result
