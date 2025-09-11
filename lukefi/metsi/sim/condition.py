from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from lukefi.metsi.sim.operation_payload import OperationPayload
if TYPE_CHECKING:
    from lukefi.metsi.sim.generators import Treatment

T = TypeVar("T")
Predicate = Callable[[int, T], bool]


class Condition[T]:
    parent: "Treatment[T]"
    predicate: Predicate[OperationPayload[T]]

    def __init__(self, predicate: Predicate[OperationPayload[T]]) -> None:
        self.predicate = predicate

    def __call__(self, time_point: int, subject: OperationPayload[T]) -> bool:
        return self.predicate(time_point, subject)

    def __and__(self, other: "Condition[T]") -> "Condition[T]":
        return Condition(lambda t, x: self.predicate(t, x) and other.predicate(t, x))

    def __or__(self, other: "Condition[T]") -> "Condition[T]":
        return Condition(lambda t, x: self.predicate(t, x) or other.predicate(t, x))
