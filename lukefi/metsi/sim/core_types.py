from collections.abc import Callable
from copy import deepcopy, copy
from types import SimpleNamespace
from typing import TYPE_CHECKING, NamedTuple, Optional, TypeVar
import weakref

from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.operation_payload import OperationPayload
from lukefi.metsi.sim.state_tree import StateTree
if TYPE_CHECKING:
    from lukefi.metsi.sim.event import Event
    from lukefi.metsi.sim.generators import Generator


def identity(x):
    return x


class DeclaredEvents[T](NamedTuple):
    time_points: list[int]
    # generators: list[dict["GeneratorFn[T]", list[Callable[[T], T]]]] = [{}]
    treatment_generator: "Generator[T]"


class SimConfiguration[T](SimpleNamespace):
    """
    A class to manage simulation configuration, including operations, generators,
    events, and time points.
    Attributes:
        operation_params: A dictionary containing
            parameters for each operation, where the key is the operation name and
            the value is a list of parameter dictionaries.
        operation_file_params: A dictionary containing
            file-related parameters for operations, where the key is the operation
            name and the value is a dictionary of file parameters.
        events: A list of declared events for the simulation.
        run_constraints: A dictionary defining constraints for
            simulation runs, where the key is a constraint name and the value is a
            dictionary of constraint details.
        time_points: A sorted list of unique time points derived from the
            declared simulation events.
    Methods:
        __init__(**kwargs):
            Initializes the SimConfiguration instance with operation and generator
            lookups, and additional keyword arguments.
    """
    # operation_params: dict[Callable, list[dict[str, Any]]] = {}
    # operation_file_params: dict[str, dict[str, str]] = {}
    events: list[DeclaredEvents[T]] = []
    # run_constraints: dict[Callable, dict] = {}
    time_points: list[int] = []

    def __init__(self, **kwargs):
        """
        Initializes the core simulation object.
        Args:
            **kwargs: Additional keyword arguments to be passed to the parent class initializer.
        """
        super().__init__(**kwargs)
        self._populate_simulation_events(self.simulation_events)

    def _populate_simulation_events(self, events: list["Event[T]"]):
        time_points = set()
        self.events = []
        for event_set in events:
            # source_time_points = event_set.get('time_points', [])
            source_time_points = event_set.time_points
            new_event = DeclaredEvents(
                time_points=source_time_points,
                # generators=event_set.get('generators', [])
                treatment_generator=event_set.treatments
            )
            self.events.append(new_event)
            time_points.update(source_time_points)
        self.time_points = sorted(time_points)


class EventTree[T]:
    """
    Event represents a computational operation in a tree of following event paths.
    """

    __slots__ = ('wrapped_operation', 'branches', '_previous_ref', '__weakref__')

    wrapped_operation: "ProcessedOperation[T]"
    branches: list["EventTree[T]"]
    _previous_ref: Optional[weakref.ReferenceType["EventTree[T]"]]

    def __init__(self,
                 operation: Optional["ProcessedOperation[T]"] = None,
                 previous: Optional['EventTree[T]'] = None):

        self.wrapped_operation = operation or identity
        self._previous_ref = weakref.ref(previous) if previous else None
        self.branches = []

    @property
    def previous(self):
        return self._previous_ref() if self._previous_ref else None

    @previous.setter
    def previous(self, prev: Optional['EventTree[T]']):
        self._previous_ref = weakref.ref(prev) if prev else None

    def find_root(self):
        return self if self.previous is None else self.previous.find_root()

    def attach(self, previous: 'EventTree[T]'):
        self.previous = previous
        previous.add_branch(self)

    def operation_chains(self) -> list[list["ProcessedOperation[T]"]]:
        """
        Recursively produce a list of lists of possible operation chains represented by this event tree in post-order
        traversal.
        """
        if len(self.branches) == 0:
            # Yes. A leaf node returns a single chain with a single operation.
            return [[self.wrapped_operation]]
        result: list[list["ProcessedOperation[T]"]] = []
        for branch in self.branches:
            chains = branch.operation_chains()
            for chain in chains:
                result.append([self.wrapped_operation] + chain)
        return result

    def evaluate(self,
                 payload: "OperationPayload[T]",
                 state_tree: Optional[StateTree[PossiblyLayered[T]]] = None) -> list["OperationPayload[T]"]:
        """
        Recursive pre-order walkthrough of this event tree to evaluate its operations with the given payload,
        copying it for branching. If given a root node, a StateTree is also constructed, containing all complete
        intermediate states in the simulation.

        :param payload: the simulation data payload (we don't care what it is here)
        :param state_tree: optional state tree node
        :return: list of result payloads from this EventTree or as concatenated from its branches
        """
        current = self.wrapped_operation(payload)
        branching_state: StateTree | None = None
        if state_tree is not None:
            state_tree.state = deepcopy(current.computational_unit)
            state_tree.done_operation = current.operation_history[-1][1] if len(current.operation_history) > 0 else None
            state_tree.time_point = current.operation_history[-1][0] if len(current.operation_history) > 0 else None
            state_tree.operation_params = current.operation_history[-1][2] if len(
                current.operation_history) > 0 else None

        if len(self.branches) == 0:
            return [current]
        if len(self.branches) == 1:
            if state_tree is not None:
                branching_state = StateTree()
                state_tree.add_branch(branching_state)
            return self.branches[0].evaluate(current, branching_state)
        results: list["OperationPayload[T]"] = []
        for branch in self.branches:
            try:
                if state_tree is not None:
                    branching_state = StateTree()
                evaluated_branch = branch.evaluate(copy(current), branching_state)
                results.extend(evaluated_branch)
                if state_tree is not None and branching_state is not None:
                    state_tree.add_branch(branching_state)
            except UserWarning:
                ...
        if len(results) == 0:
            raise UserWarning("Branch aborted with all children failing")
        return results

    def add_branch(self, et: 'EventTree[T]'):
        et.previous = self
        self.branches.append(et)

    def add_branch_from_operation(self, operation: "ProcessedOperation[T]"):
        self.add_branch(EventTree(operation, self))


T = TypeVar("T")
Evaluator = Callable[[OperationPayload[T], EventTree[T]], list[OperationPayload[T]]]
Runner = Callable[[OperationPayload[T], SimConfiguration, Evaluator[T]], list[OperationPayload[T]]]
ProcessedOperation = Callable[[OperationPayload[T]], OperationPayload[T]]
ProcessedGenerator = Callable[[Optional[list[EventTree[T]]]], list[EventTree[T]]]
