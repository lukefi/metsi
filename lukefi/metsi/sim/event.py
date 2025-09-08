from collections.abc import Callable
from typing import Any, Optional, TypeVar
from typing import Sequence as Sequence_

from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.core_types import EventTree, OpTuple, ProcessedOperation
from lukefi.metsi.sim.generators import alternatives, sequence

T = TypeVar('T')  # T = ForestStand

Condition = Callable[[T], bool]
GeneratorFn = Callable[[Optional[list[EventTree[T]]], ProcessedOperation[T]], list[EventTree[T]]]
TreatmentFn = Callable[[OpTuple[PossiblyLayered[T]]], OpTuple[PossiblyLayered[T]]]


class GeneratorBase:
    pass


class Treatment[T](GeneratorBase):
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


class Generator[T](GeneratorBase):
    generator_fn: GeneratorFn[T]
    treatments: Sequence_[GeneratorBase]


class Sequence[T](Generator[T]):
    def __init__(self, treatments: Sequence_[GeneratorBase]):
        self.generator_fn = sequence
        self.treatments = treatments


class Alternatives[T](Generator[T]):
    def __init__(self, treatments: Sequence_[GeneratorBase]):
        self.generator_fn = alternatives
        self.treatments = treatments


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
