import unittest
import forestry.aggregate_utils as aggutil
from collections import OrderedDict
from copy import deepcopy

class AggregateUtilsTest(unittest.TestCase):

    simulation_aggregates = {
        'operation_results': {
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
        'current_time_point': 10
    }

    def test_get_operation_results(self):
        result = aggutil._get_operation_results(self.simulation_aggregates)
        self.assertEqual(self.simulation_aggregates['operation_results'], result)

    def test_get_operation_aggregates(self):
        result = aggutil.get_operation_aggregates(self.simulation_aggregates, 'oper1')
        self.assertEqual(OrderedDict({ 0: {'a': 111} }), result)

    def test_get_latest_operation_aggregate(self):
        result = aggutil.get_latest_operation_aggregate(self.simulation_aggregates, 'oper2')
        self.assertEqual({'c': 333}, result)

    def test_store_operation_aggregate(self):
        fixture = deepcopy(self.simulation_aggregates)
        fixture['operation_results']['oper3'] = OrderedDict({ 10: {'d': 999} })

        new_aggregate = { 'd': 999 }
        result = aggutil.store_operation_aggregate(self.simulation_aggregates, new_aggregate, 'oper3')
        self.assertEqual(fixture, result)
