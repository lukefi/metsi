from dataclasses import dataclass
import unittest
from collections import OrderedDict
from copy import deepcopy
from sim.core_types import AggregatedResults

class AggregateUtilsTest(unittest.TestCase):

    simulation_aggregates = AggregatedResults(
        operation_results = {
            'oper1': OrderedDict(
                {
                    0: {
                        'a': 111
                    }
                }
            ),
            'oper2': OrderedDict(
                    {
                        0: {
                            'b': 222
                        },
                        5: {
                            'c': 333
                        }
                    }
                ),
        },
        current_time_point = 10
    )

    def test_get_latest_operation_aggregate(self):
        result = self.simulation_aggregates.prev('oper2')
        self.assertEqual({'c': 333}, result)

    def test_store_operation_aggregate(self):
        fixture = deepcopy(self.simulation_aggregates)
        fixture.operation_results['oper3'] = OrderedDict({ 10: {'d': 999} })
        new_aggregate = { 'd': 999 }
        result = deepcopy(self.simulation_aggregates)
        result.store('oper3', new_aggregate)
        self.assertEqual(fixture.operation_results, result.operation_results)

    def test_modify_deepcopied_list_item_does_not_modify_original(self):
        @dataclass
        class Dummy:
            value: str

        original = AggregatedResults(
            operation_results = {
                'oper1': [Dummy(1), Dummy(2)],
            },
            current_time_point = 1
        )

        #modifying an attribute of copy does not modify original
        copied = deepcopy(original)
        copied.operation_results["oper1"][0].value = 4
        self.assertEqual(original.operation_results["oper1"][0].value, 1)
