"""
This module contains a collection of util functions and dummy payload functions for test cases
"""
import unittest
from typing import Any, Optional
from collections.abc import Callable
import numpy as np

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.sim.collected_data import OpTuple
from lukefi.metsi.sim.simulation_payload import SimulationPayload

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


def collecting_increment(input: OpTuple[int], **operation_params) -> OpTuple[int]:
    incrementation = operation_params.get('incrementation', 1)
    state, collected_data = input
    previous_collected_data = collected_data.prev('collecting_increment')
    new_collected_data = {'run_count': 1} if previous_collected_data is None else {'run_count': previous_collected_data['run_count'] + 1}
    collected_data.store('collecting_increment', new_collected_data)
    return state + incrementation, collected_data


def inc(x: SimulationPayload[int]) -> SimulationPayload[int]:
    x.computational_unit += 1
    return x


def dec(x: int) -> int:
    return x - 1


def max_reducer(x: list[int]) -> Optional[int]:
    return max(x)


def grow_dummy(f: float, d: float, h: float, dd: float) -> tuple[float, float, float]:
    return f-f%100, d+dd/500, h+dd/1000


def parametrized_operation(x: SimulationPayload[int], **kwargs) -> SimulationPayload[int]:
    if kwargs.get('amplify') is True:
        x.computational_unit *= 1000
    return x

def parametrized_operation_using_file_parameter(x, **kwargs):
    file_path = kwargs.get("dummy_file")
    file_contents = open(file_path, "r").read()
    if file_contents == "kissa123\n":
        return file_contents
    else:
        return x

def collect_results(payloads: list[SimulationPayload]) -> list:
    return list(map(lambda payload: payload.computational_unit, payloads))


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def get_default_timber_price_table() -> str:
    return open("tests/resources/timber_price_table.csv", "r").read()


def prepare_growth_test_stand():
    stand = ForestStand(
        identifier="123",
        area=20.3,
        soil_peatland_category=1,
        site_type_category=1,
        tax_class_reduction=1,
        land_use_category=1,
        geo_location=(6656996.0, 310260.0, 10.0, "EPSG:3067"),
        reference_trees_pre_vec=[
            ReferenceTree(species=TreeSpecies.PINE, stems_per_ha=123, breast_height_diameter=30, height=20, biological_age=55, breast_height_age=15, sapling=False),
            ReferenceTree(species=TreeSpecies.SPRUCE, stems_per_ha=123, breast_height_diameter=25, height=17, biological_age=37, breast_height_age=15, sapling=False),
            ReferenceTree(species=TreeSpecies.PINE, stems_per_ha=123, breast_height_diameter=0, height=0.3, biological_age=1, breast_height_age=0, sapling=True)
        ],
        year=2025
    )
    return stand


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
