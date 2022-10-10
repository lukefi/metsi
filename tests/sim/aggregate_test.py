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
