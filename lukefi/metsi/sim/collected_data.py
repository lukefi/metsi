from collections import OrderedDict
from copy import deepcopy
from typing import Any, Optional, TypeVar

from lukefi.metsi.data.layered_model import PossiblyLayered


class CollectedData:

    def __init__(
        self,
        treatment_results: Optional[dict[str, Any]] = None,
        current_time_point: Optional[int] = None,
        initial_time_point: Optional[int] = None
    ):
        self.operation_results: dict[str, Any] = treatment_results or {}
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
            treatment_results={k: self._copy_op_results(v) for k, v in self.operation_results.items()},
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


T = TypeVar("T")
OpTuple = tuple[PossiblyLayered[T], CollectedData]
