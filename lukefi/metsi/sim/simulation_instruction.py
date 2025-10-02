from copy import deepcopy
from typing import Optional, TypeVar

from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.generators import Alternatives, GeneratorBase, Generator, Sequence
from lukefi.metsi.sim.simulation_payload import SimulationPayload

T = TypeVar('T')  # T = ForestStand


class SimulationInstruction[T]:
    time_points: list[int]
    conditions: list[Condition[SimulationPayload[T]]]
    event_generator: Generator[T]

    def __init__(self, time_points: list[int], events: Generator[T] | list[GeneratorBase] | set[GeneratorBase],
                 conditions: Optional[list[Condition[SimulationPayload[T]]]] = None) -> None:
        self.time_points = time_points
        if isinstance(events, Generator):
            self.event_generator = events
        elif isinstance(events, list):
            self.event_generator = Sequence(events)
        elif isinstance(events, set):
            self.event_generator = Alternatives(list(events))
        if conditions is not None:
            self.conditions = conditions
        else:
            self.conditions = []


def generator_declarations_for_time_point(
        simulation_instructions: list[SimulationInstruction[T]], time: int) -> list[Generator[T]]:
    """
    From events declarations, find the EventTree generators declared for the given time point.

    :param events: list of DeclaredEvents objects for generator declarations and time points
    :param time: point of simulation time for selecting matching generators
    :return: list of generator declarations for the desired point of time
    """
    generator_declarations: list[Generator[T]] = []
    for instruction in simulation_instructions:
        if time in instruction.time_points:
            generator_copy = deepcopy(instruction.event_generator)
            generator_copy.time_point = time
            generator_declarations.append(generator_copy)
    return generator_declarations
