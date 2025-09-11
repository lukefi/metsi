from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from lukefi.metsi.sim.generators import Treatment

T = TypeVar("T")
Predicate = Callable[[int, T], bool]


class Condition[T, P]:
    parent: "Treatment[T]"
    predicate: Predicate[P]

    def __init__(self, predicate: Predicate[P]) -> None:
        self.predicate = predicate

    def __call__(self, time_point: int, subject: P) -> bool:
        return self.predicate(time_point, subject)

    def __and__(self, other: "Condition[T, P]") -> "Condition[T, P]":
        return Condition(lambda t, x: self.predicate(t, x) and other.predicate(t, x))

    def __or__(self, other: "Condition[T, P]") -> "Condition[T, P]":
        return Condition(lambda t, x: self.predicate(t, x) or other.predicate(t, x))
