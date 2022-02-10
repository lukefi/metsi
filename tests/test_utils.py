"""
This module contains a collection of util functions and dummy payload functions for test cases
"""

from typing import Any, List, Optional


def raises(x: Any) -> None:
    raise Exception("Run failure")


def identity(x: Any) -> Any:
    return x


def none(x: Any) -> None:
    return None


def inc(x: int) -> int:
    return x + 1


def dec(x: int) -> int:
    return x - 1


def max_reducer(x: List[int]) -> Optional[int]:
    return max(x)


def parametrized_operation(x, **kwargs):
    if kwargs.get('amplify') is True:
        return x * 1000
    else:
        return x
