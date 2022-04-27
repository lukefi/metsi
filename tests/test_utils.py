"""
This module contains a collection of util functions and dummy payload functions for test cases
"""
import os
from typing import Any, List, Optional

import yaml

from sim.core_types import OperationPayload


def raises(x: Any) -> None:
    raise Exception("Run failure")


def identity(x: Any) -> Any:
    return x


def none(x: Any) -> None:
    return None


def aggregating_increment(input: tuple[int, dict]) -> tuple[int, dict]:
    state, previous = input
    aggregate = {'run_count': 1} if previous is None else {'run_count': previous['run_count'] + 1}
    return state + 1, aggregate


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


def collect_results(payloads: List[OperationPayload]) -> List:
    return list(map(lambda payload: payload.simulation_state, payloads))


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def load_yaml(file_name: str) -> dict:
    return yaml.load(file_contents(os.path.join(os.getcwd(), "tests", "resources", file_name)), Loader=yaml.CLoader)
