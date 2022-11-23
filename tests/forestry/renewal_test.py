import unittest
from forestry.renewal import cost_only_renewal
from sim.core_types import AggregatedResults
from forestdatamodel.model import ForestStand

class RenewalTest(unittest.TestCase):

    def test_cost_only_renewal(self):
        payload = (
            ForestStand(area=10),
            AggregatedResults()
        )
        operation_parameters = {
            "operations": ["410", "510"],
            "renewal_cost_table": "tests/resources/renewal_operation_pricing.csv"
        }

        _, aggrs = cost_only_renewal(payload, **operation_parameters)
        self.assertEqual(aggrs.get("renewal")["410"][0], 1000)
        self.assertEqual(aggrs.get("renewal")["510"][0], 1000)