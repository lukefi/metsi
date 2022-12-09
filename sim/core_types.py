from collections import OrderedDict, defaultdict
from copy import deepcopy
from types import SimpleNamespace
from typing import Callable, Optional, Any, TypeVar, Generic


def identity(x):
    return x


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
        operation_results: Optional[dict[str, Any]] = None,
        current_time_point: Optional[int] = None
    ):
        self.operation_results: dict[str, Any] = operation_results or {}
        self.current_time_point: int = current_time_point or 0

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

    def __deepcopy__(self, memo: dict) -> "AggregatedResults":
        return AggregatedResults(
            operation_results = {k: self._copy_op_results(v) for k,v in self.operation_results.items()},
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

    def get_list_result(self, tag: str) -> list[Any]:
        try:
            return self.operation_results[tag]
        except KeyError:
            self.operation_results[tag] = []
            return self.operation_results[tag]

    def extend_list_result(self, tag: str, aggr: list[Any]):
        self.get_list_result(tag).extend(aggr)

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
