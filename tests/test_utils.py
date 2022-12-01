"""
This module contains a collection of util functions and dummy payload functions for test cases
"""
import os
import unittest
from typing import Any, Optional, Callable
import numpy as np

import yaml

from sim.core_types import OpTuple, OperationPayload


class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: list[tuple], fn: Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)


def raises(x: Any) -> None:
    raise Exception("Run failure")


def identity(x: Any) -> Any:
    return x


def none(x: Any) -> None:
    return None


def aggregating_increment(input: OpTuple[int], **operation_params) -> OpTuple[int]:
    incrementation = operation_params.get('incrementation', 1)
    state, aggregates = input
    latest_aggregate = aggregates.prev('aggregating_increment')
    aggregate = {'run_count': 1} if latest_aggregate is None else {'run_count': latest_aggregate['run_count'] + 1}
    aggregates.store('aggregating_increment', aggregate)
    return state + incrementation, aggregates


def inc(x: int) -> int:
    return x + 1


def dec(x: int) -> int:
    return x - 1


def max_reducer(x: list[int]) -> Optional[int]:
    return max(x)


def grow_dummy(f: float, d: float, h: float, dd: float) -> tuple[float, float, float]:
    return f-f%100, d+dd/500, h+dd/1000


def parametrized_operation(x, **kwargs):
    if kwargs.get('amplify') is True:
        return x * 1000
    else:
        return x

def parametrized_operation_using_file_parameter(x, **kwargs):
    file_path = kwargs.get("dummy_file")
    file_contents = open(file_path, "r").read()
    if file_contents == "kissa123\n":
        return file_contents
    else:
        return x

def collect_results(payloads: list[OperationPayload]) -> list:
    return list(map(lambda payload: payload.simulation_state, payloads))


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def load_yaml(file_name: str) -> dict:
    return yaml.load(file_contents(os.path.join(os.getcwd(), "tests", "resources", file_name)), Loader=yaml.CLoader)
    

DEFAULT_TIMBER_PRICE_TABLE = np.array(
                        [[  1., 160., 370.,  55.],
                        [  1., 160., 400.,  57.],
                        [  1., 160., 430.,  59.],
                        [  1., 160., 460.,  59.],
                        [  2.,  70., 300.,  17.]])


TIMBER_PRICE_TABLE_THREE_GRADES = np.array(
                        [[  1., 160., 370.,  55.],
                        [  1., 160., 400.,  57.],
                        [  1., 160., 430.,  59.],
                        [  1., 160., 460.,  59.],
                        [  2.,  70., 300.,  17.],
                        [  2.,  70., 270.,  15.],
                        [  3.,  70., 220.,  10.]
                        ])
