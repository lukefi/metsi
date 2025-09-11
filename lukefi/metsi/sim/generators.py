from abc import ABC, abstractmethod
import os
from typing import Any, Optional, TypeVar, override
from typing import Sequence as Sequence_

from collections.abc import Callable
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.sim.event_tree import EventTree
from lukefi.metsi.sim.operation_payload import ProcessedOperation
from lukefi.metsi.sim.operations import prepared_processor, prepared_operation
from lukefi.metsi.app.utils import MetsiException

T = TypeVar("T")

GeneratorFn = Callable[[Optional[list[EventTree[T]]], ProcessedOperation[T]], list[EventTree[T]]]
TreatmentFn = Callable[[OpTuple[T]], OpTuple[T]]
Condition = Callable[[T], bool]
ProcessedGenerator = Callable[[Optional[list[EventTree[T]]]], list[EventTree[T]]]


class GeneratorBase[T](ABC):
    """Shared abstract base class for Generator and Treatment types."""
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
    """Generator for sequential treatments."""

    @override
    def unwrap(self, parents: list[EventTree], time_point: int) -> list[EventTree]:
        current = parents
        for child in self.children:
            current = child.unwrap(current, self.time_point or time_point)
        return current


class Alternatives[T](Generator[T]):
    """Generator for branching treatments"""

    @override
    def unwrap(self, parents: list[EventTree], time_point: int) -> list[EventTree]:
        retval = []
        for child in self.children:
            retval.extend(child.unwrap(parents, self.time_point or time_point))
        return retval


class Treatment[T](GeneratorBase):
    """Base class for treatments. Contains conditions and parameters and the actual function that operates on the
    simulation state."""
    conditions: list[Condition[T]]
    parameters: dict[str, Any]
    file_parameters: dict[str, str]
    run_constraints: dict[str, Any]
    treatment_fn: TreatmentFn[T]

    def __init__(self, treatment_fn: TreatmentFn[T], parameters: Optional[dict[str, Any]] = None,
                 conditions: Optional[list[Condition[T]]] = None,
                 file_parameters: Optional[dict[str, str]] = None,
                 run_constraints: Optional[dict[str, Any]] = None) -> None:
        self.treatment_fn = treatment_fn

        if parameters is not None:
            self.parameters = parameters
        else:
            self.parameters = {}

        if file_parameters is not None:
            self.file_parameters = file_parameters
        else:
            self.file_parameters = {}

        if run_constraints is not None:
            self.run_constraints = run_constraints
        else:
            self.run_constraints = {}

        if conditions is not None:
            self.conditions = conditions
        else:
            self.conditions = []

    def unwrap(self, parents: list[EventTree], time_point: int) -> list[EventTree]:
        retval = []
        for parent in parents:
            branch = EventTree(self._prepare_paremeterized_treatment(time_point))
            parent.add_branch(branch)
            retval.append(branch)
        return retval

    def _prepare_paremeterized_treatment(self, time_point) -> ProcessedOperation[T]:
        self._check_file_params()
        combined_params = self._merge_params()
        return prepared_processor(self.treatment_fn, time_point, self.run_constraints, **combined_params)

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


def simple_processable_chain(operation_tags: list[Callable[[T], T]],
                             operation_params: dict[Callable[[T], T], Any]) -> list[Callable[[T], T]]:
    """Prepare a list of partially applied (parametrized) operation functions based on given declaration of operation
    tags and operation parameters"""
    result: list[Callable[[T], T]] = []
    for tag in operation_tags if operation_tags is not None else []:
        params = operation_params.get(tag, [{}])
        if len(params) > 1:
            raise MetsiException(f"Trying to apply multiple parameter set for preprocessing operation \'{tag}\'. "
                                 "Defining multiple parameter sets is only supported for alternative clause "
                                 "generators.")
        result.append(prepared_operation(tag, **params[0]))
    return result
