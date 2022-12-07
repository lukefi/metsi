import unittest
import yaml


class YamlLibraryTestSuite(unittest.TestCase):
    simple_test_fixture = """
    object_one:
      property_one: 1
      primitive_collection:
        - item1
        - item2
      object_collection:
        - param1: abc
          param2: def
        - param1: yes
          param2: no 
    """

    anchors_test_fixture = """
    variables:
      var_one: &var_one 1
    object_one:
      property_one: *var_one
    """

    aliases_test_fixture = """
    named_generators:
      alternatives: &seeding_alternatives
        - seed: &seed_pine
            - species: 'pine'
              spread: 0.3
        - seed: &seed_birch
            - species: 'birch'
              spread: 0.2 

    simulation_events:
      - time_points: [0]
        generators:
          - alternatives: *seeding_alternatives
          - sequence:
              - seed: *seed_pine
              - seed: *seed_birch
    """

    def test_simple_yaml_load(self):
        result = yaml.load(self.simple_test_fixture, Loader=yaml.CLoader)
        self.assertEqual(1, result['object_one']['property_one'])
        self.assertEqual(2, len(result['object_one']['primitive_collection']))
        self.assertEqual('item1', result['object_one']['primitive_collection'][0])
        self.assertEqual('item2', result['object_one']['primitive_collection'][1])
        self.assertEqual('abc', result['object_one']['object_collection'][0]['param1'])
        self.assertEqual('def', result['object_one']['object_collection'][0]['param2'])
        self.assertEqual(True, result['object_one']['object_collection'][1]['param1'])
        self.assertEqual(False, result['object_one']['object_collection'][1]['param2'])

    def test_anchors_yaml_load(self):
        result = yaml.load(self.anchors_test_fixture, Loader=yaml.CLoader)
        self.assertEqual(1, result['variables']['var_one'])
        self.assertEqual(1, result['object_one']['property_one'])

    def test_aliases(self):
        result = yaml.load(self.aliases_test_fixture, Loader=yaml.CLoader)
        expected_event = {
            'time_points': [0],
            'generators': [
                {'alternatives': [
                        {'seed': [{'species': 'pine', 'spread': 0.3}]},
                        {'seed': [{'species': 'birch', 'spread': 0.2}]}
                ]},
                {'sequence': [
                        {'seed': [{'species': 'pine', 'spread': 0.3}]},
                        {'seed': [{'species': 'birch', 'spread': 0.2}]}
                ]}
            ]
        }

        self.maxDiff = None
        self.assertDictEqual(expected_event, result['simulation_events'][0])
