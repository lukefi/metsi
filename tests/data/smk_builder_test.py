import unittest
import os
from lukefi.metsi.data.formats.ForestBuilder import ForestCentreBuilder
from lukefi.metsi.data.enums.internal import *

builder_flags = {
    'strata_origin': '1'
}
smk_data = 'SMK_source.xml'
absolute_resource_path = os.path.join(os.getcwd(), 'tests', 'data', 'resources', smk_data)

class TestForestCentreBuilder(unittest.TestCase):

    with open(absolute_resource_path, 'r', encoding='utf-8') as f:
        xml_string = f.read()
    smk_builder = ForestCentreBuilder(builder_flags, xml_string)
    smk_stands = smk_builder.build()

    def test_individual_smk_build_with_different_strata_origins(self):
        assertions = [
            ('1', 3),
            ('2', 2),
            (None, 0)
        ]
        for i in assertions:
            smk_builder = ForestCentreBuilder(
                {
                    'strata_origin': i[0]
                },
                self.xml_string)
            stands = smk_builder.build()
            number_of_stratums = len(stands[0].tree_strata)
            self.assertEqual(i[1], number_of_stratums)

    def test_smk_builder_stands(self):
        self.assertEqual(2, len(self.smk_stands))

    def test_smk_builder_stand_identifiers(self):
        self.assertEqual('10', self.smk_stands[0].identifier)
        self.assertEqual('15', self.smk_stands[1].identifier)

    def test_smk_builder_stand_variables(self):
        # TODO: implement parse logic for management unit id
        self.assertEqual(None, self.smk_stands[0].management_unit_id)
        self.assertEqual(None, self.smk_stands[1].management_unit_id)
        self.assertEqual(2020, self.smk_stands[0].year)
        self.assertEqual(2020, self.smk_stands[1].year)
        self.assertEqual(0.28, self.smk_stands[0].area)
        self.assertEqual(0.45, self.smk_stands[1].area)
        self.assertEqual(0.28, self.smk_stands[0].area_weight)
        self.assertEqual(0.45, self.smk_stands[1].area_weight)
        self.assertEqual((6542843.0, 532437.0, None, 'EPSG:3067'), self.smk_stands[0].geo_location)
        self.assertEqual((6532843.0, 536437.0, None, 'EPSG:3067'), self.smk_stands[1].geo_location)
        self.assertEqual('10', self.smk_stands[0].identifier)
        self.assertEqual('15', self.smk_stands[1].identifier)
        # TODO: verify the default value of degree days
        self.assertEqual(None, self.smk_stands[0].degree_days)
        self.assertEqual(None, self.smk_stands[1].degree_days)
        # TODO: verify the default value of owner category
        self.assertEqual(OwnerCategory.PRIVATE, self.smk_stands[0].owner_category)
        self.assertEqual(OwnerCategory.PRIVATE, self.smk_stands[1].owner_category)
        # st:MainGroup '1' -> 1
        self.assertEqual(1, self.smk_stands[0].land_use_category)
        # st:MainGroup '1' -> 1
        self.assertEqual(1, self.smk_stands[1].land_use_category)
        # st:SubGroup '1' -> 1
        self.assertEqual(SoilPeatlandCategory.PINE_MIRE, self.smk_stands[0].soil_peatland_category)
        # st:SubGroup '3' -> 3
        self.assertEqual(3, self.smk_stands[1].soil_peatland_category)
        # st:FertilityClass '3' -> 3
        self.assertEqual(SiteType.DAMP_SITE, self.smk_stands[0].site_type_category)
        # st:FertilityClass '3' -> 3
        self.assertEqual(SiteType.SUB_DRY_SITE, self.smk_stands[1].site_type_category)
        # TODO: verify the default value of tax class reduction
        self.assertEqual(0, self.smk_stands[0].tax_class_reduction)
        self.assertEqual(0, self.smk_stands[1].tax_class_reduction)
        # TODO: verify the default value of tax class
        self.assertEqual(0, self.smk_stands[0].tax_class)
        self.assertEqual(0, self.smk_stands[1].tax_class)
        # st:DrainageState '1' -> 0
        self.assertEqual(DrainageCategory.TRANSFORMED_MIRE, self.smk_stands[0].drainage_category)
        # st:DrainageState '9' -> 5
        self.assertEqual(DrainageCategory.TRANSFORMED_MIRE, self.smk_stands[1].drainage_category)
        # Drainage feasibility default value True
        self.assertEqual(True, self.smk_stands[0].drainage_feasibility)
        self.assertEqual(True, self.smk_stands[1].drainage_feasibility)
        # TODO: implement parse logic for drainage year
        self.assertEqual(None, self.smk_stands[0].drainage_year)
        self.assertEqual(None, self.smk_stands[1].drainage_year)
        # TODO: implement parse logic for fertilization year
        self.assertEqual(None, self.smk_stands[0].fertilization_year)
        self.assertEqual(None, self.smk_stands[1].fertilization_year)
        # TODO: implement parse logic for soil surface preparation year
        self.assertEqual(None, self.smk_stands[0].soil_surface_preparation_year)
        self.assertEqual(None, self.smk_stands[1].soil_surface_preparation_year)
        # Natural regeneration feasibility default value False
        self.assertEqual(False, self.smk_stands[0].natural_regeneration_feasibility)
        self.assertEqual(False, self.smk_stands[1].natural_regeneration_feasibility)
        # TODO implement parse logic for regeneration area cleaning year
        self.assertEqual(None, self.smk_stands[0].regeneration_area_cleaning_year)
        self.assertEqual(None, self.smk_stands[1].regeneration_area_cleaning_year)
        # Development class default value 0
        self.assertEqual(0, self.smk_stands[0].development_class)
        self.assertEqual(0, self.smk_stands[1].development_class)
        # TODO implement parse logic for artificial regeneration year
        self.assertEqual(None, self.smk_stands[0].artificial_regeneration_year)
        self.assertEqual(None, self.smk_stands[1].artificial_regeneration_year)
        # TODO implement parse logic for young stand tending year
        self.assertEqual(None, self.smk_stands[0].young_stand_tending_year)
        self.assertEqual(None, self.smk_stands[1].young_stand_tending_year)
        # TODO implement parse logic for pruning year
        self.assertEqual(None, self.smk_stands[0].pruning_year)
        self.assertEqual(None, self.smk_stands[1].pruning_year)
        # TODO implement parse logic for cutting year
        self.assertEqual(None, self.smk_stands[0].cutting_year)
        self.assertEqual(None, self.smk_stands[1].cutting_year)
        self.assertEqual(-1, self.smk_stands[0].forestry_centre_id)
        self.assertEqual(-1, self.smk_stands[1].forestry_centre_id)
        # st:CuttingRestriction '0' -> 1
        self.assertEqual(1, self.smk_stands[0].forest_management_category)
        # st:CuttingRestriction '0' -> 1
        self.assertEqual(1, self.smk_stands[1].forest_management_category)
        # TODO implement parse logic for last cutting method
        self.assertEqual(None, self.smk_stands[0].method_of_last_cutting)
        self.assertEqual(None, self.smk_stands[1].method_of_last_cutting)
        self.assertEqual(-1, self.smk_stands[0].municipality_id)
        self.assertEqual(-1, self.smk_stands[1].municipality_id)
        self.assertEqual(9.5, self.smk_stands[0].basal_area)
        self.assertEqual(0.0, self.smk_stands[1].basal_area)


    def test_smk_builder_strata(self):
        self.assertEqual(3, len(self.smk_stands[0].tree_strata))
        self.assertEqual(0, len(self.smk_stands[1].tree_strata))

    def test_smk_builder_stratum_identifiers(self):
        self.assertEqual('10.1-stratum', self.smk_stands[0].tree_strata[0].identifier)
        self.assertEqual('10.2-stratum', self.smk_stands[0].tree_strata[1].identifier)
        self.assertEqual(0, len(self.smk_stands[1].tree_strata))

    def test_smk_builder_stratum_variables(self):
        # tst:TreeSpecies '1' -> 1
        self.assertEqual(TreeSpecies.SPRUCE, self.smk_stands[0].tree_strata[0].species)
        # tst:TreeSpecies '2' -> 2
        self.assertEqual(TreeSpecies.SPRUCE, self.smk_stands[0].tree_strata[1].species)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].origin)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].origin)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].stems_per_ha)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].stems_per_ha)
        # tst:MeanDiameter '24.1' -> 24.1
        self.assertEqual(2.0, self.smk_stands[0].tree_strata[0].mean_diameter)
        # tst:MeanDiameter '22.0' -> 22.0
        self.assertEqual(13.1, self.smk_stands[0].tree_strata[1].mean_diameter)
        # tst:MeanHeight '20.5' -> 20.5
        self.assertEqual(2.3, self.smk_stands[0].tree_strata[0].mean_height)
        # tst:MeanHeight '19.0' -> 19.0
        self.assertEqual(12.2, self.smk_stands[0].tree_strata[1].mean_height)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].breast_height_age)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].breast_height_age)
        # tst:MeanHeight '62' -> 62
        self.assertEqual(10.0, self.smk_stands[0].tree_strata[0].biological_age)
        # tst:MeanHeight '62' -> 62
        self.assertEqual(48.0, self.smk_stands[0].tree_strata[1].biological_age)
        # tst:BasalArea '10.1' -> 10.1
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].basal_area)
        # tst:BasalArea '10.5' -> 10.5
        self.assertEqual(5.2, self.smk_stands[0].tree_strata[1].basal_area)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].saw_log_volume_reduction_factor)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].saw_log_volume_reduction_factor)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].cutting_year)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].cutting_year)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].age_when_10cm_diameter_at_breast_height)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].age_when_10cm_diameter_at_breast_height)
        # tst:StratumNumber '1' -> 1
        self.assertEqual(1, self.smk_stands[0].tree_strata[0].tree_number)
        # tst:StratumNumber '2' -> 2
        self.assertEqual(2, self.smk_stands[0].tree_strata[1].tree_number)
        self.assertEqual((0.0, 0.0, 0.0), self.smk_stands[0].tree_strata[1].stand_origin_relative_position)
        self.assertEqual((0.0, 0.0, 0.0), self.smk_stands[0].tree_strata[1].stand_origin_relative_position)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].lowest_living_branch_height)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].lowest_living_branch_height)
        self.assertEqual(None, self.smk_stands[0].tree_strata[0].management_category)
        self.assertEqual(None, self.smk_stands[0].tree_strata[1].management_category)
        self.assertEqual(Storey.REMOTE, self.smk_stands[0].tree_strata[0].storey)
        self.assertEqual(Storey.REMOTE, self.smk_stands[0].tree_strata[1].storey)
