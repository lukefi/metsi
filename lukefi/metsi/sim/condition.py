from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")
Predicate = Callable[[int, T], bool]


class Condition[T]:
    predicate: Predicate[T]

    def __init__(self, predicate: Predicate[T]) -> None:
        self.predicate = predicate

    def __call__(self, time_point: int, subject: T) -> bool:
        return self.predicate(time_point, subject)

    def __and__(self, other: "Condition[T]") -> "Condition[T]":
        return Condition(lambda t, x: self.predicate(t, x) and other.predicate(t, x))

    def __or__(self, other: "Condition[T]") -> "Condition[T]":
        return Condition(lambda t, x: self.predicate(t, x) or other.predicate(t, x))
