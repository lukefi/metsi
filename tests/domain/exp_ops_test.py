import unittest
from unittest.mock import Mock
from lukefi.metsi.data.model import ReferenceTree, ForestStand, TreeStratum
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.data.conversion.internal2mela import mela_stand
from lukefi.metsi.app.utils import ConfigurationException
from lukefi.metsi.domain.exp_ops import prepare_rst_output, classify_values_to
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.enums.mela import MelaTreeSpecies

class TestExpOps(unittest.TestCase):

    def setUp(self):
        # Create mock data for testing
        self.stand1 = Mock(
            spec=ForestStand,
            reference_trees=[
                Mock(spec=ReferenceTree, is_living=Mock(return_value=True)),
                Mock(spec=ReferenceTree, is_living=Mock(return_value=False))
            ],
            is_forest_land=Mock(return_value=True),
            is_auxiliary=Mock(return_value=False),
            has_trees=Mock(return_value=True),
            has_strata=Mock(return_value=False)
        )
        self.stand2 = Mock(
            spec=ForestStand,
            reference_trees=[
                Mock(spec=ReferenceTree, is_living=Mock(return_value=True)),
                Mock(spec=ReferenceTree, is_living=Mock(return_value=True))
            ],
            is_forest_land=Mock(return_value=False),
            is_auxiliary=Mock(return_value=True),
            has_trees=Mock(return_value=False),
            has_strata=Mock(return_value=False)
        )
        self.stands = StandList([self.stand1, self.stand2])

    def test_prepare_rst_output(self):
        result = prepare_rst_output(self.stands)
        self.assertEqual(len(result), 1)  # Only one stand should remain
        self.assertEqual(len(result[0].reference_trees), 1)  # Only living trees should remain

    def test_classify_values_to_valid_format(self):
        # Dummy data
        stand = ForestStand(
            geo_location=(6654200, 102598, 0.0, "EPSG:3067"),
            area_weight=100.0,
            auxiliary_stand=True)
        stand.reference_trees.append(
            ReferenceTree(species=TreeSpecies.SPRUCE, stand=stand))
        stand.tree_strata.append(
            TreeStratum(species=TreeSpecies.PINE, stand=stand))
        
        # fixture
        operation_params = {'format': 'rst'}

        # test
        result = classify_values_to([stand], **operation_params)
        self.assertEqual(len(result), 1)


    def test_classify_values_to_invalid_format(self):
        operation_params = {'format': 'invalid_format'}
        with self.assertRaises(ConfigurationException):
            classify_values_to(self.stands, **operation_params)
