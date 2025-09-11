from copy import deepcopy
from typing import Optional, TypeVar

from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.generators import Alternatives, GeneratorBase, Generator, Sequence
from lukefi.metsi.sim.operation_payload import OperationPayload

T = TypeVar('T')  # T = ForestStand


class Event[T]:
    time_points: list[int]
    conditions: list[Condition[T, OperationPayload[T]]]
    treatment_generator: Generator[T]

    def __init__(self, time_points: list[int], treatments: Generator[T] | list[GeneratorBase] | set[GeneratorBase],
                 conditions: Optional[list[Condition[T, OperationPayload[T]]]] = None) -> None:
        self.time_points = time_points
        if isinstance(treatments, Generator):
            self.treatment_generator = treatments
        elif isinstance(treatments, list):
            self.treatment_generator = Sequence(treatments)
        elif isinstance(treatments, set):
            self.treatment_generator = Alternatives(list(treatments))
        if conditions is not None:
            self.conditions = conditions
        else:
            self.conditions = []


def generator_declarations_for_time_point(events: list[Event[T]], time: int) -> list[Generator[T]]:
    """
    From events declarations, find the EventTree generators declared for the given time point.

    :param events: list of DeclaredEvents objects for generator declarations and time points
    :param time: point of simulation time for selecting matching generators
    :return: list of generator declarations for the desired point of time
    """
    generator_declarations: list[Generator[T]] = []
    for event in events:
        if time in event.time_points:
            generator_copy = deepcopy(event.treatment_generator)
            generator_copy.time_point = time
            generator_declarations.append(generator_copy)
    return generator_declarations
