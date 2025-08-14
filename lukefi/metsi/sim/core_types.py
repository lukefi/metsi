from collections import OrderedDict
from collections.abc import Callable
from copy import deepcopy, copy
from types import SimpleNamespace
from typing import NamedTuple, Optional, Any, TypeVar
import weakref

from lukefi.metsi.data.layered_model import LayeredObject, PossiblyLayered


def identity(x):
    return x


class DeclaredEvents[T](NamedTuple):
    time_points: list[int] = []
    generators: list[dict["GeneratorFn[T]", list[Callable[[T], T]]]] = [{}]


class SimConfiguration(SimpleNamespace):
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
    operation_params: dict[Callable, list[dict[str, Any]]] = {}
    operation_file_params: dict[str, dict[str, str]] = {}
    events: list[DeclaredEvents] = []
    run_constraints: dict[Callable, dict] = {}
    time_points: list[int] = []

    def __init__(self, **kwargs):
        """
        Initializes the core simulation object.
        Args:
            **kwargs: Additional keyword arguments to be passed to the parent class initializer.
        """
        super().__init__(**kwargs)
        self._populate_simulation_events(self.simulation_events)

    def _populate_simulation_events(self, events: list):
        time_points = set()
        self.events = []
        for event_set in events:
            source_time_points = event_set.get('time_points', [])
            new_event = DeclaredEvents(
                time_points=source_time_points,
                generators=event_set.get('generators', [])
            )
            self.events.append(new_event)
            time_points.update(source_time_points)
        self.time_points = sorted(time_points)


class EventTree[T]:
    """
    Event represents a computational operation in a tree of following event paths.
    """

    __slots__ = ('operation', 'branches', '_previous_ref', '__weakref__')

    operation: Callable[[T], T]
    branches: list["EventTree[T]"]
    _previous_ref: Optional[weakref.ReferenceType["EventTree[T]"]]

    def __init__(self,
                 operation: Optional[Callable[[T], T]] = None,
                 previous: Optional['EventTree[T]'] = None):

        self.operation = operation or identity
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

    def operation_chains(self) -> list[list[Callable[[T], T]]]:
        """
        Recursively produce a list of lists of possible operation chains represented by this event tree in post-order
        traversal.
        """
        if len(self.branches) == 0:
            # Yes. A leaf node returns a single chain with a single operation.
            return [[self.operation]]
        result: list[list[Callable[[T], T]]] = []
        for branch in self.branches:
            chains = branch.operation_chains()
            for chain in chains:
                result.append([self.operation] + chain)
        return result

    def evaluate(self, payload: T) -> list[T]:
        """
        Recursive pre-order walkthrough of this event tree to evaluate its operations with the given payload,
        copying it for branching.

        :param payload: the simulation data payload (we don't care what it is here)
        :return: list of result payloads from this EventTree or as concatenated from its branches
        """
        current = self.operation(payload)
        if len(self.branches) == 0:
            return [current]
        if len(self.branches) == 1:
            return self.branches[0].evaluate(current)
        results: list[T] = []
        for branch in self.branches:
            try:
                results.extend(branch.evaluate(copy(current)))
            except UserWarning:
                ...
        if len(results) == 0:
            raise UserWarning("Branch aborted with all children failing")
        return results

    def add_branch(self, et: 'EventTree[T]'):
        et.previous = self
        self.branches.append(et)

    def add_branch_from_operation(self, operation: Callable[[T], T]):
        self.add_branch(EventTree(operation, self))


class CollectedData:

    def __init__(
        self,
        operation_results: Optional[dict[str, Any]] = None,
        current_time_point: Optional[int] = None,
        initial_time_point: Optional[int] = None
    ):
        self.operation_results: dict[str, Any] = operation_results or {}
        self.current_time_point: int = current_time_point or initial_time_point or 0
        self.initial_time_point: int = initial_time_point or 0

    def _copy_op_results(self, value: Any) -> dict | list:
        """
        optimises the deepcopy of self by shallow copying dict and list type operation_results.
        This relies on the assumption that an operation result is not modified after it's stored.
        """
        if isinstance(value, dict):
            return OrderedDict(value.items())
        if isinstance(value, list):
            return list(value)
        return deepcopy(value)

    def __copy__(self) -> "CollectedData":
        return CollectedData(
            operation_results={k: self._copy_op_results(v) for k, v in self.operation_results.items()},
            current_time_point=self.current_time_point,
            initial_time_point=self.initial_time_point
        )

    def prev(self, tag: str) -> Any:
        try:
            return next(reversed(self.operation_results[tag].values()))
        except (KeyError, StopIteration):
            return None

    def get(self, tag: str) -> Any:
        try:
            return self.operation_results[tag]
        except KeyError:
            self.operation_results[tag] = OrderedDict()
            return self.operation_results[tag]

    def store(self, tag: str, collected_data: Any):
        self.get(tag)[self.current_time_point] = collected_data

    def get_list_result(self, tag: str) -> list[Any]:
        try:
            return self.operation_results[tag]
        except KeyError:
            self.operation_results[tag] = []
            return self.operation_results[tag]

    def extend_list_result(self, tag: str, collected_data: list[Any]):
        self.get_list_result(tag).extend(collected_data)

    def upsert_nested(self, value, *keys):
        """
        Upsert a value under a key path in a nested dictionary (under self.operation_results).
        :param value: The value to upsert.
        :param keys: The key path to the value to be upserted. Lenght of keys must be
        larger than 1; this method is not intended to be used for upserting values  directly
        under operation_results.
        """
        def _upsert(d: dict, value: dict, *keys):
            if len(keys) == 1:
                try:
                    if keys[0] in d.keys():
                        # a dictionary will be updated with a dictionary,
                        # but other types will overrider the existing value
                        if isinstance(value, dict) and isinstance(d[keys[0]], dict):
                            d[keys[0]].update(value)
                        else:
                            d[keys[0]] = value
                    else:
                        d[keys[0]] = value
                except KeyError:
                    d[keys[0]] = value
                return d

            key = keys[0]
            d[key] = _upsert(d.get(key, {}), value, *keys[1:])
            return d

        if len(keys) < 2:
            raise ValueError("At least two keys must be provided.")

        _upsert(self.get(keys[0]), value, *keys[1:])


class OperationPayload[T](SimpleNamespace):
    """Data structure for keeping simulation state and progress data. Passed on as the data package of chained
    operation calls. """
    computational_unit: PossiblyLayered[T]
    collected_data: CollectedData
    operation_history: list[tuple[int, "Operation[T]", dict[str, dict]]]

    def __copy__(self) -> "OperationPayload[T]":
        copy_like: PossiblyLayered[T]
        if isinstance(self.computational_unit, LayeredObject):
            copy_like = self.computational_unit.new_layer()
            copy_like.reference_trees = [tree.new_layer() for tree in copy_like.reference_trees]
            copy_like.tree_strata = [stratum.new_layer() for stratum in copy_like.tree_strata]
        else:
            copy_like = deepcopy(self.computational_unit)

        return OperationPayload(
            computational_unit=copy_like,
            collected_data=copy(self.collected_data),
            operation_history=list(self.operation_history)
        )


T = TypeVar("T")
OpTuple = tuple[T, CollectedData]
Evaluator = Callable[[T, EventTree[T]], list[T]]
Runner = Callable[[T, SimConfiguration, Evaluator[T]], list[T]]
GeneratorFn = Callable[[Optional[list[EventTree[T]]]], list[EventTree[T]]]
Operation = Callable[[OpTuple[PossiblyLayered[T]]], OpTuple[PossiblyLayered[T]]]
ProcessedOperation = Callable[[OperationPayload[T]], OperationPayload[T]]
