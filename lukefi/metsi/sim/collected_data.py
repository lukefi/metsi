from collections import OrderedDict
from copy import deepcopy
from typing import Any, Optional, TypeVar

from lukefi.metsi.data.layered_model import PossiblyLayered


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


T = TypeVar("T")
OpTuple = tuple[PossiblyLayered[T], CollectedData]
