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


    def test_list_result_deepcopy(self):
        """
        Ensures that appending to a deepcopied list of operation_results does not modify the source list.
        """
        @dataclass
        class Dummy:
            value: str

        original = AggregatedResults(
            operation_results = {
                'oper1': [Dummy(1), Dummy(2)],
            },
            current_time_point = 1
        )

        copied = deepcopy(original)
        copied.operation_results['oper1'].append(Dummy(3))

        self.assertEqual(len(original.operation_results["oper1"]), 2)
        self.assertEqual(len(copied.operation_results["oper1"]), 3)


    def test_upsert_nested(self):
        aggrs = deepcopy(self.simulation_aggregates)

        # insert a new dict under a new key will create a new key
        aggrs.upsert_nested({'e': 444}, 'oper2', 10)
        self.assertEqual({'e': 444}, aggrs.operation_results['oper2'][10])
        self.assertEqual(list(aggrs.operation_results['oper2'].keys()), [0, 5, 10])

        # inserting a new dict under an existing key will update the dict under the key
        aggrs.upsert_nested({'f': 555}, 'oper2', 10)
        self.assertEqual({'e': 444, 'f': 555}, aggrs.operation_results['oper2'][10])

        # if the value at key was previously a dict but now an int is passed, the dict will be overwritten
        aggrs.upsert_nested(555, 'oper2', 10)
        self.assertEqual(555, aggrs.operation_results['oper2'][10])

        # if the value at key was previously an int but now a dict is passed, the int will be overwritten
        aggrs.upsert_nested(666, 'oper2', 15)
        aggrs.upsert_nested({'g': 777}, 'oper2', 15)
        self.assertEqual({'g': 777}, aggrs.operation_results['oper2'][15])

        # a new value can be inserted at any depth
        aggrs.upsert_nested({'h': 888}, 'oper2', "deeply", "nested", "key")
        self.assertEqual({'h': 888}, aggrs.operation_results['oper2']['deeply']['nested']['key'])

        # len(keys) must be greater than 1, otherwise ValueError is raised
        self.assertRaises(ValueError, aggrs.upsert_nested, {'i': 999}, *['oper2'])
        self.assertRaises(ValueError, aggrs.upsert_nested, [{'i': 999}])
