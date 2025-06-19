from collections import OrderedDict
from copy import deepcopy, copy
from types import SimpleNamespace
from typing import Optional, Any, TypeVar, Generic
from collections.abc import Callable
import weakref
def identity(x):
    return x


class DeclaredEvents(SimpleNamespace):
    time_points: list[int] = []
    generators: list[dict] = [{}]


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
    operation_params: dict[str, list[dict[str, Any]]] = {}
    operation_file_params: dict[str, dict[str, str]] = {}
    events: list[DeclaredEvents] = []
    run_constraints: dict[str, dict] = {}
    time_points = []

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
        self.events = list()
        for event_set in events:
            source_time_points = event_set.get('time_points', [])
            new_event = DeclaredEvents(
                time_points=source_time_points,
                generators=event_set.get('generators', [])
            )
            self.events.append(new_event)
            time_points.update(source_time_points)
        self.time_points = sorted(time_points)


class EventTree:
    """
    Event represents a computational operation in a tree of following event paths.
    """

    __slots__ = ('operation', 'branches', '_previous_ref', '__weakref__') 

    def __init__(self, 
                 operation: Optional[Callable[[Optional[Any]], Optional[Any]]] = None,
                 previous: Optional['EventTree'] = None):

        self.operation = operation if operation is not None else identity
        self._previous_ref = weakref.ref(previous) if previous else None
        self.branches = []

    @property
    def previous(self):
        return self._previous_ref() if self._previous_ref else None
    
    @previous.setter
    def previous(self, prev: Optional['EventTree']):
        self._previous_ref = weakref.ref(prev) if prev else None


    def find_root(self: 'EventTree'):
        return self if self.previous is None else self.previous.find_root()
        
    def attach(self, previous: 'EventTree'):
        self.previous = previous
        previous.add_branch(self)

    def operation_chains(self):
        """
        Recursively produce a list of lists of possible operation chains represented by this event tree in post-order
        traversal.
        """
        if len(self.branches) == 0:
            # Yes. A leaf node returns a single chain with a single operation.
            return [[self.operation]]
        else:
            result = []
            for branch in self.branches:
                chains = branch.operation_chains()
                for chain in chains:
                    result.append([self.operation] + chain)
            return result

    def evaluate(self, payload) -> list:
        """
        Recursive pre-order walkthrough of this event tree to evaluate its operations with the given payload,
        copying it for branching.

        :param payload: the simulation data payload (we don't care what it is here)
        :return: list of result payloads from this EventTree or as concatenated from its branches
        """
        current = self.operation(payload)
        if len(self.branches) == 0:
            return [current]
        elif len(self.branches) == 1:
            return self.branches[0].evaluate(current)
        elif len(self.branches) > 1:
            results = []
            for branch in self.branches:
                try:
                    results.extend(branch.evaluate(copy(current)))
                except UserWarning:
                    ...
            if len(results) == 0:
                raise UserWarning(f"Branch aborted with all children failing")
            else:
                return results

    def add_branch(self, et: 'EventTree'):
        et.previous = self
        self.branches.append(et)

    def add_branch_from_operation(self, operation: Callable):
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

    def _copy_op_results(self, value: Any) -> dict or list:
        """
        optimises the deepcopy of self by shallow copying dict and list type operation_results.
        This relies on the assumption that an operation result is not modified after it's stored.
        """
        if isinstance(value, dict):
            return OrderedDict(value.items())
        elif isinstance(value, list):
            return list(value)
        else:
            return deepcopy(value)

    def __copy__(self) -> "CollectedData":
        return CollectedData(
            operation_results={k: self._copy_op_results(v) for k,v in self.operation_results.items()},
            current_time_point=self.current_time_point,
            initial_time_point=self.initial_time_point
        )

    def prev(self, tag: str) -> Any:
        try:
            return next(reversed(self.operation_results[tag].values()))
        except (KeyError, StopIteration):
            return None

    def get(self, tag: str) -> OrderedDict[int, Any]:
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
        def _upsert(d:dict, value: dict, *keys):
            if len(keys) == 1:
                try:
                    if keys[0] in d.keys():
                        # a dictionary will be updated with a dictionary, but other types will overrider the existing value
                        if isinstance(value, dict) and isinstance(d[keys[0]], dict):
                            d.get(keys[0]).update(value)
                        else:
                            d[keys[0]] = value
                    else:
                        d[keys[0]] = value
                except KeyError:
                    d[keys[0]] = value
                return d
            else:
                key = keys[0]
                d[key] = _upsert(d.get(key, {}), value, *keys[1:])
                return d

        if len(keys) < 2:
            raise ValueError("At least two keys must be provided.")

        _upsert(self.get(keys[0]), value, *keys[1:])

CUType = TypeVar("CUType")  # CU for Computational Unit


class OperationPayload(SimpleNamespace, Generic[CUType]):
    """Data structure for keeping simulation state and progress data. Passed on as the data package of chained
    operation calls. """
    computational_unit: CUType
    collected_data: CollectedData
    operation_history: list[tuple[int, str, dict[str, dict]]]

    def __copy__(self) -> "OperationPayload":
        try:
            copy_like = self.computational_unit.new_layer()
            copy_like.reference_trees = [tree.new_layer() for tree in copy_like.reference_trees]
            copy_like.tree_strata = [stratum.new_layer() for stratum in copy_like.tree_strata]
        except:
            copy_like = deepcopy(self.computational_unit)

        return OperationPayload(
            computational_unit = copy_like,
            collected_data = copy(self.collected_data),
            operation_history = list(self.operation_history)
        )


OpTuple = tuple[CUType, CollectedData]
SourceData = list[CUType]
Evaluator = Callable[[OperationPayload[CUType]], list[OperationPayload[CUType]]]
Runner = Callable[[OperationPayload[CUType], dict, dict, Evaluator[CUType]], list[OperationPayload[CUType]]]
GeneratorFn = Callable[[Optional[list[EventTree]]], list[EventTree]]
