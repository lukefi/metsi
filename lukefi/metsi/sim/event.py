from collections.abc import Callable
from typing import Optional, TypeVar

from lukefi.metsi.sim.generators import Alternatives, GeneratorBase, Generator, Sequence

T = TypeVar('T')  # T = ForestStand

Condition = Callable[[T], bool]


class Event[T]:
    time_points: list[int]
    conditions: list[Condition[T]]
    treatments: Generator[T]

    def __init__(self, time_points: list[int], treatments: Generator[T] | list[GeneratorBase] | set[GeneratorBase],
                 conditions: Optional[list[Condition[T]]] = None) -> None:
        self.time_points = time_points
        if isinstance(treatments, Generator):
            self.treatments = treatments
        elif isinstance(treatments, list):
            self.treatments = Sequence(treatments)
        elif isinstance(treatments, set):
            self.treatments = Alternatives(list(treatments))
        if conditions is not None:
            self.conditions = conditions
        else:
            self.conditions = []
