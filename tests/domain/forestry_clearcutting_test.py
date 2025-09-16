import unittest
from lukefi.metsi.data.model import ReferenceTree,ForestStand
import lukefi.metsi.domain.forestry_operations.clearcutting_limits as clearcutting_lim
import lukefi.metsi.domain.forestry_operations.clearcut as clearcut
from lukefi.metsi.forestry import forestry_utils as futil
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.domain.forestry_operations.thinning_limits import SpeciesKey
from lukefi.metsi.sim.collected_data import CollectedData
import lukefi.metsi.domain.forestry_operations.planting as plnt
from lukefi.metsi.domain.utils.enums import SiteTypeKey

class ClearcuttingTest(unittest.TestCase):

    def generate_stand_fixture(self,d13=32,h=25,age=90,sitetype=3,treelist=[1,1,1,2,2,2,1,1,1],rl=200) -> ForestStand:
        species = [TreeSpecies(i) for i in treelist]
        diameters = [d13 + i for i in range(0, len(treelist))]
        heights = [h + i for i in range(0, len(treelist))]
        stems = [rl - i for i in range(0, len(treelist))]
        ages = [age + i for i in range(0, len(treelist))]
        ids = [str(x) for x in range(0,len(treelist))]
        stand = ForestStand()
        stand.area = 2.5
        stand.site_type_category = sitetype
        stand.soil_peatland_category = 1
        stand.reference_trees = [
            ReferenceTree(identifier=id,species=s, breast_height_diameter=d, stems_per_ha=f,biological_age=a,height=h)
            for id,s, d, f, a,h in zip(ids,species, diameters, stems, ages,heights)
        ]
        return stand


    def test_create_clearcutting_limits_table(self):
        # thinning_limits = open('tests/resources/thinning_limits.txt', 'r').read()
        table_ages = clearcutting_lim.create_clearcutting_limits_table('data/parameter_files/renewal_ages_southernFI.txt')
        self.assertEqual(len(table_ages), 4)
        self.assertEqual(len(table_ages[0]), 5)
        self.assertEqual(int(table_ages[1][3]), 50)

    def test_get_clearcutting_limits_dict_ages(self):
        ages = clearcutting_lim.get_clearcutting_agelimits_from_parameter_file_contents('data/parameter_files/renewal_ages_southernFI.txt')
        self.assertEqual(ages[SiteTypeKey.OMT][SpeciesKey.DOWNY_BIRCH],50)
        self.assertEqual(ages[SiteTypeKey.CT][SpeciesKey.PINE],90)

    def test_get_clearcutting_limits_dict_diameters(self):
        diameters = clearcutting_lim.get_clearcutting_diameterlimits_from_parameter_file_contents('data/parameter_files/renewal_diameters_southernFI.txt')
        self.assertEqual(diameters[SiteTypeKey.OMT][SpeciesKey.DOWNY_BIRCH],23.0)
        self.assertEqual(diameters[SiteTypeKey.CT][SpeciesKey.PINE],22.0)

    def test_get_regeneration_instructions_dict(self):
        instructions = plnt.get_planting_instructions_from_parameter_file_contents('tests/resources/planting_test/planting_instructions.txt')
        self.assertEqual(instructions[SiteTypeKey.OMT]["species"],1)

    def test_get_clearcutting_limits(self):
        stand = self.generate_stand_fixture()
        mean_d13 = futil.calculate_basal_area_weighted_attribute_sum(stand.reference_trees,
        f=lambda x: x.breast_height_diameter*futil.calculate_basal_area(x))
        self.assertEqual(36.33495699307285, mean_d13)
        self.assertEqual(93.96598639455782, futil.mean_age_stand(stand))
        self.assertEqual(70, clearcutting_lim.get_clearcutting_limits(stand,'data/parameter_files/renewal_ages_southernFI.txt','data/parameter_files/renewal_diameters_southernFI.txt')[0])
        self.assertEqual(26, clearcutting_lim.get_clearcutting_limits(stand,'data/parameter_files/renewal_ages_southernFI.txt','data/parameter_files/renewal_diameters_southernFI.txt')[1])

    def test_clearcut_with_output(self):
        stand = self.generate_stand_fixture()
        collected_data = CollectedData()
        stand, collected_data = clearcut._clearcut_with_output(stand, collected_data, 'clearcutting')
        self.assertEqual(192, collected_data.get_list_result("felled_trees")[-1].stems_per_ha)
        self.assertEqual("clearcutting", collected_data.get_list_result("felled_trees")[-1].operation)
        self.assertEqual(33.0,collected_data.get_list_result("felled_trees")[-1].height)

    def test_clearcutting(self):
        stand = self.generate_stand_fixture()
        operation_parameters = {'clearcutting_limits_ages': 'data/parameter_files/renewal_ages_southernFI.txt','clearcutting_limits_diameters':'data/parameter_files/renewal_diameters_southernFI.txt'}
        collected_data = CollectedData()
        oper_input = (stand, collected_data)
        stand, collected_data = clearcut.clearcutting(oper_input, **operation_parameters)
        self.assertEqual(0, futil.overall_stems_per_ha(stand.reference_trees))
        self.assertEqual(0, futil.mean_age_stand(stand))
        self.assertEqual(192, collected_data.get_list_result("felled_trees")[-1].stems_per_ha)
