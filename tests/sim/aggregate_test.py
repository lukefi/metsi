import unittest
from collections import OrderedDict
from copy import deepcopy
from lukefi.metsi.sim.collected_data import CollectedData

class AggregateUtilsTest(unittest.TestCase):

    collected_data = CollectedData(
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

    def test_get_latest_operation_collected_data(self):
        result = self.collected_data.prev('oper2')
        self.assertEqual({'c': 333}, result)

    def test_store_operation_collected_data(self):
        fixture = deepcopy(self.collected_data)
        fixture.operation_results['oper3'] = OrderedDict({ 10: {'d': 999} })
        new_collected_data = { 'd': 999 }
        result = deepcopy(self.collected_data)
        result.store('oper3', new_collected_data)
        self.assertEqual(fixture.operation_results, result.operation_results)
