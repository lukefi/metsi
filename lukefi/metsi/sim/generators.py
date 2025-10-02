from abc import ABC, abstractmethod
import os
from typing import Any, Optional, TypeVar, override
from typing import Sequence as Sequence_

from collections.abc import Callable
from lukefi.metsi.sim.operations import prepared_operation
from lukefi.metsi.sim.processor import processor
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.event_tree import EventTree
from lukefi.metsi.sim.simulation_payload import SimulationPayload, ProcessedTreatment
from lukefi.metsi.app.utils import MetsiException

T = TypeVar("T")

GeneratorFn = Callable[[Optional[list[EventTree[T]]], ProcessedTreatment[T]], list[EventTree[T]]]
TreatmentFn = Callable[[OpTuple[T]], OpTuple[T]]
ProcessedGenerator = Callable[[Optional[list[EventTree[T]]]], list[EventTree[T]]]


class GeneratorBase[T](ABC):
    """Shared abstract base class for Generator and Event types."""
    @abstractmethod
    def unwrap(self, parents: list[EventTree[T]], time_point: int) -> list[EventTree[T]]:
        pass


class Generator[T](GeneratorBase, ABC):
    """Abstract base class for generator types."""
    children: Sequence_[GeneratorBase]
    time_point: Optional[int]

    def __init__(self, children: Sequence_[GeneratorBase], time_point: Optional[int] = None):
        self.children = children
        self.time_point = time_point

    def compose_nested(self) -> EventTree[T]:
        """
        Generate a simulation EventTree using the given NestableGenerator.

        :param nestable_generator: NestableGenerator tree for generating a EventTree.
        :return: The root node of the generated EventTree
        """
        root: EventTree[T] = EventTree()
        self.unwrap([root], 0)
        return root


class Sequence[T](Generator[T]):
    """Generator for sequential events."""

    @override
    def unwrap(self, parents: list[EventTree], time_point: int) -> list[EventTree]:
        current = parents
        for child in self.children:
            current = child.unwrap(current, self.time_point or time_point)
        return current


class Alternatives[T](Generator[T]):
    """Generator for branching events"""

    @override
    def unwrap(self, parents: list[EventTree], time_point: int) -> list[EventTree]:
        retval = []
        for child in self.children:
            retval.extend(child.unwrap(parents, self.time_point or time_point))
        return retval


class Event[T](GeneratorBase):
    """Base class for events. Contains conditions and parameters and the actual treatment function that operates on the
    simulation state."""
    preconditions: list[Condition[SimulationPayload[T]]]
    postconditions: list[Condition[SimulationPayload[T]]]
    parameters: dict[str, Any]
    file_parameters: dict[str, str]
    treatment: TreatmentFn[T]

    def __init__(self, treatment: TreatmentFn[T], parameters: Optional[dict[str, Any]] = None,
                 preconditions: Optional[list[Condition[SimulationPayload[T]]]] = None,
                 postconditions: Optional[list[Condition[SimulationPayload[T]]]] = None,
                 file_parameters: Optional[dict[str, str]] = None) -> None:
        self.treatment = treatment

        if parameters is not None:
            self.parameters = parameters
        else:
            self.parameters = {}

        if file_parameters is not None:
            self.file_parameters = file_parameters
        else:
            self.file_parameters = {}

        if preconditions is not None:
            self.preconditions = preconditions
        else:
            self.preconditions = []

        if postconditions is not None:
            self.postconditions = postconditions
        else:
            self.postconditions = []

    @override
    def unwrap(self, parents: list[EventTree], time_point: int) -> list[EventTree]:
        retval = []
        for parent in parents:
            branch = EventTree(self._prepare_paremeterized_treatment(time_point))
            parent.add_branch(branch)
            retval.append(branch)
        return retval

    def _prepare_paremeterized_treatment(self, time_point) -> ProcessedTreatment[T]:
        self._check_file_params()
        combined_params = self._merge_params()
        prepared_treatment = prepared_operation(self.treatment, **combined_params)
        return lambda payload: processor(payload, prepared_treatment, self.treatment, time_point,
                                         self.preconditions, self.postconditions, **combined_params)

    def _check_file_params(self):
        for _, path in self.file_parameters.items():
            if not os.path.isfile(path):
                raise FileNotFoundError(f"file {path} defined in operation_file_params was not found")

    def _merge_params(self) -> dict[str, Any]:
        common_keys = self.parameters.keys() & self.file_parameters.keys()
        if common_keys:
            raise MetsiException(
                f"parameter(s) {common_keys} were defined both in 'parameters' and 'file_parameters' sections "
                "in control.py. Please change the name of one of them.")
        return self.parameters | self.file_parameters  # pipe is the merge operator
