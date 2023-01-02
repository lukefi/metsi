import unittest
from types import SimpleNamespace

from lukefi.metsi.domain.data_collection.marshalling import collect_properties
from lukefi.metsi.sim.core_types import CollectedData
from tests.test_utils import prepare_growth_test_stand


class CollectPropertiesTest(unittest.TestCase):
    def generate_fixture(self):
        class TestObj(SimpleNamespace):
            a = 1
            b = 2
            time_point = 0

        stand = prepare_growth_test_stand()
        collected_data = CollectedData(initial_time_point=0)
        collected_data.extend_list_result("testlist", [TestObj(), TestObj(a=3, b=4)])
        optuple = (stand, collected_data)
        return optuple

    def test_stand_collection(self):
        optuple = self.generate_fixture()
        params = {
            "stand": ["identifier", "area", "soil_peatland_category"]
        }

        _, collected_data = collect_properties(optuple, **params)
        results = collected_data.get('collect_properties')[0]
        self.assertEqual(1, len(results))
        self.assertEqual(3, len(results[0]))

    def test_tree_collection(self):
        optuple = self.generate_fixture()
        params = {
            "tree": ["stems_per_ha", "biological_age"]
        }

        _, collected_data = collect_properties(optuple, **params)
        results = collected_data.get('collect_properties')[0]
        self.assertEqual(3, len(results))
        for r in results:
            self.assertEqual(2, len(r))

    def test_list_collection(self):
        optuple = self.generate_fixture()
        params = {
            "testlist": ["a", "b"]
        }

        _, collected_data = collect_properties(optuple, **params)
        results = collected_data.get('collect_properties')[0]
        self.assertEqual(2, len(results))
        for r in results:
            self.assertEqual(2, len(r))

    def test_failure_cases(self):
        optuple = self.generate_fixture()
        fail_params = [
            {'stand': 'abc'},
            {'tree': 223},
            {'unknown_list': ['a']}
        ]
        for params in fail_params:
            self.assertRaises(Exception, collect_properties, **params)


