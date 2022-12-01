from collections import OrderedDict
from copy import deepcopy
from types import SimpleNamespace
from typing import Callable, Optional, Any, TypeVar, Generic


def identity(x):
    return x


class SimulationEvent(SimpleNamespace):
    time_points: list[int] = []
    generators: list[dict] = {}


class SimConfiguration(SimpleNamespace):
    operation_lookup: dict[str, Callable] = {}
    operation_params: dict[str, list[dict[str, Any]]] = {}
    operation_file_params: dict[str, dict[str, str]] = {}
    events: list[SimulationEvent] = []
    run_constraints: dict[str, dict] = {}
    time_points = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.populate_simulation_events(self.simulation_events)

    def populate_simulation_events(self, events: list):
        time_points = set()
        self.events = list()
        for event_set in events:
            source_time_points = event_set.get('time_points', [])
            new_event = SimulationEvent(
                time_points=source_time_points,
                generators=event_set.get('generators', [])
            )
            self.events.append(new_event)
            time_points.update(source_time_points)
        self.time_points = sorted(list(time_points))


class Step:
    """
    Step represents a computational operation in a tree of alternative computation paths.
    """
    operation: Callable = identity  # default to the identity function, essentially no-op
    branches: list['Step'] = []
    previous: 'Step' or None = None

    def __init__(self, operation: Callable[[Optional[Any]], Optional[Any]] or None = None,
                 previous: 'Step' or None = None):
        self.operation = operation if operation is not None else identity
        self.previous = previous
        self.branches = []

    def find_root(self: 'Step'):
        return self if self.previous is None else self.previous.find_root()

    def attach(self, previous: 'Step'):
        self.previous = previous
        previous.add_branch(self)

    def operation_chains(self):
        """
        Recursively produce a list of lists of possible operation chains represented by this tree in post-order
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

    def add_branch(self, step: 'Step'):
        step.previous = self
        self.branches.append(step)

    def add_branch_from_operation(self, operation: Callable):
        self.add_branch(Step(operation, self))


class AggregatedResults:

    def __init__(
        self,
        operation_results: Optional[dict[str, OrderedDict[int, Any]]] = None,
        current_time_point: Optional[int] = None
    ):
        self.operation_results: dict[str, OrderedDict[int, Any]] = operation_results or {}
        self.current_time_point: int = current_time_point or 0

    def __deepcopy__(self, memo: dict) -> "AggregatedResults":
        return AggregatedResults(
            operation_results = {k: OrderedDict(v.items()) for k,v in self.operation_results.items()},
            current_time_point = self.current_time_point
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

    def store(self, tag: str, aggr: Any):
        self.get(tag)[self.current_time_point] = aggr


CUType = TypeVar("CUType")  # CU for Computational Unit


class OperationPayload(SimpleNamespace, Generic[CUType]):
    """Data structure for keeping simulation state and progress data. Passed on as the data package of chained
    operation calls. """
    simulation_state: CUType
    aggregated_results: AggregatedResults
    operation_history: list[tuple[int, str, dict[str, dict]]]

    def __deepcopy__(self, memo: dict) -> "OperationPayload":
        return OperationPayload(
            simulation_state = deepcopy(self.simulation_state, memo),
            aggregated_results = deepcopy(self.aggregated_results, memo),
            operation_history = list(self.operation_history)
        )


OpTuple = tuple[CUType, AggregatedResults]
SourceData = list[CUType]
StrategyRunner = Callable[[OperationPayload[CUType], dict, dict], list[OperationPayload[CUType]]]
GeneratorFn = Callable[[Optional[list[Step]]], list[Step]]
