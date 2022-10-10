import unittest
from forestdatamodel.model import ReferenceTree,ForestStand
import forestry.clearcutting_limits as clearcutting_lim
import forestry.clearcut as clearcut
from forestryfunctions import forestry_utils as futil
from forestdatamodel.enums.internal import TreeSpecies
import forestry.aggregate_utils as aggutil
from collections import OrderedDict
from forestry import cross_cutting as cross_cut
from forestry.aggregate_utils import get_latest_operation_aggregate,get_operation_aggregates

from forestry.thinning_limits import SiteTypeKey, SpeciesKey

class ClearcuttingTest(unittest.TestCase):

    def test_stand(self,d13=20,age=40,sitetype=3,treelist=[1,1,1,2,2,2,3,3,3],rl=200) -> ForestStand:
        species = [TreeSpecies(i) for i in treelist]
        diameters = [d13 + i for i in range(0, len(treelist))]
        heights = [25.0 + i for i in range(0, len(treelist))]
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
   
    def read_clearcutting_limits_file(self,ages,instructions):
        if ages:
            return open('data/parameter_files/renewal_ages_southernFI.txt', 'r').read()
        elif instructions:
             return open('data/parameter_files/clearcut_instructions.txt', 'r').read()
        else:
            return open('data/parameter_files/renewal_diameters_southernFI.txt', 'r').read()
    
    def test_create_clearcutting_limits_table(self):
        # thinning_limits = open('tests/resources/thinning_limits.txt', 'r').read()
        table = clearcutting_lim.create_clearcutting_limits_table(self.read_clearcutting_limits_file(ages=True,instructions=False))
        self.assertEqual(len(table), 4)
        self.assertEqual(len(table[0]), 5)
        self.assertEqual(int(table[1][3]), 50)
    
    def test_get_clearcutting_limits_dict_ages(self):
        ages = clearcutting_lim.get_clearcutting_agelimits_from_parameter_file_contents(self.read_clearcutting_limits_file(ages=True,instructions=False))
        self.assertEqual(ages[SiteTypeKey.OMT][SpeciesKey.DOWNY_BIRCH],50)
        self.assertEqual(ages[SiteTypeKey.CT][SpeciesKey.PINE],90)

    def test_get_clearcutting_limits_dict_diameters(self):
        diameters = clearcutting_lim.get_clearcutting_diameterlimits_from_parameter_file_contents(self.read_clearcutting_limits_file(ages=False,instructions=False))
        self.assertEqual(diameters[SiteTypeKey.OMT][SpeciesKey.DOWNY_BIRCH],23.0)
        self.assertEqual(diameters[SiteTypeKey.CT][SpeciesKey.PINE],22.0)

    def test_clearcutting(self):
        age_limits = self.read_clearcutting_limits_file(ages=True,instructions=False)
        diameter_limits = self.read_clearcutting_limits_file(ages=False,instructions=False)
        instructions = self.read_clearcutting_limits_file(ages=False,instructions=True)
        operation_parameters = {'clearcutting_limits_ages': age_limits,'clearcutting_limits_diameters':diameter_limits,
        'clearcutting_instructions':instructions}
        tree_variables = [
            {
                'identifier': '1',
                'species': TreeSpecies.SPRUCE,
                'breast_height_diameter': 25.0,
                'stems_per_ha': 250.0,
                'biological_age' :90
            },
            {   
                'identifier': '2',
                'species': TreeSpecies.PINE,
                'breast_height_diameter': 30.0,
                'stems_per_ha': 150.0,
                'biological_age' :90
            },
            {   
                'identifier': '3',
                'species': TreeSpecies.SPRUCE,
                'breast_height_diameter': 23.0,
                'stems_per_ha': 400.0,
                'biological_age' :90
            }
        ]
        stand_variables = {
            'site_type_category': 1,
            'soil_peatland_category': 1
        }
        stand = ForestStand(**stand_variables)
        stand.reference_trees = [ReferenceTree(**tv) for tv in tree_variables]
        self.assertEqual(800, futil.overall_stems_per_ha(stand))
        self.assertEqual(90, clearcutting_lim.mean_age_stand(stand))
        self.assertEqual(TreeSpecies.SPRUCE, futil.solve_dominant_species(stand))
        simulation_aggregates = {
            'operation_results': {},
            'current_time_point': 0,
            'current_operation_tag': 'clearcutting'
        }
        oper_input = (stand, simulation_aggregates)
        self.assertEqual(2,clearcutting_lim.get_clearcutting_instructions(stand,operation_parameters['clearcutting_instructions'])['species'])
        (stand_now,aggregates) = clearcut.clearcutting(oper_input, **operation_parameters)
        self.assertEqual(2001, futil.overall_stems_per_ha(stand_now))
        self.assertEqual(250, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['1']['stems_removed_per_ha'])
        self.assertEqual(400, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['3']['stems_removed_per_ha'])
        self.assertEqual(25, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['1']['breast_height_diameter'])
        self.assertEqual(23, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['3']['breast_height_diameter'])
    
    def test_clearcut_and_plant_output(self):
        age_limits = self.read_clearcutting_limits_file(ages=True,instructions=False)
        diameter_limits = self.read_clearcutting_limits_file(ages=False,instructions=False)
        instructions = self.read_clearcutting_limits_file(ages=False,instructions=True)
        operation_parameters = {'clearcutting_limits_ages': age_limits,'clearcutting_limits_diameters':diameter_limits,
        'clearcutting_instructions':instructions}
        stand = self.test_stand(d13=25,age=50,sitetype=4,treelist=[3,3,3,3,3,1,1,3,3],rl=80)
        self.assertEqual(TreeSpecies.SILVER_BIRCH,stand.reference_trees[0].species)
        self.assertEqual(684, futil.overall_stems_per_ha(stand))
        self.assertEqual(53.91228070175438, clearcutting_lim.mean_age_stand(stand))
        self.assertEqual(TreeSpecies.SILVER_BIRCH, futil.solve_dominant_species(stand))
        simulation_aggregates = {
            'operation_results': {},
            'current_time_point': 0,
            'current_operation_tag': 'clearcutting'
        }
        oper_input = (stand, simulation_aggregates)
        (stand,aggregates) = clearcut.clearcut(stand)
        self.assertEqual(0, futil.overall_stems_per_ha(stand))
        self.assertEqual(79, aggregates['clearcut_output']['1']['stems_removed_per_ha'])
        self.assertEqual(77, aggregates['clearcut_output']['3']['stems_removed_per_ha'])
        self.assertEqual(26, aggregates['clearcut_output']['1']['breast_height_diameter'])
        self.assertEqual(28, aggregates['clearcut_output']['3']['breast_height_diameter'])
        instructions_regen = clearcutting_lim.get_clearcutting_instructions(stand,instructions)
        self.assertEqual(instructions_regen['species'],TreeSpecies.PINE)
        (stand,regeneration_description) = clearcut.plant(stand,TreeSpecies.PINE,10,200,clearcut.SoilPreparationKey.MOUNDING)
        self.assertEqual(TreeSpecies.PINE,regeneration_description['species'])
        self.assertEqual(2000,regeneration_description['stems_per_ha'])

    def test_clearcutting_output_volumes(self):
        age_limits = self.read_clearcutting_limits_file(ages=True,instructions=False)
        diameter_limits = self.read_clearcutting_limits_file(ages=False,instructions=False)
        instructions = self.read_clearcutting_limits_file(ages=False,instructions=True)
        operation_parameters = {'clearcutting_limits_ages': age_limits,'clearcutting_limits_diameters':diameter_limits,
        'clearcutting_instructions':instructions}
        stand = self.test_stand(d13=28,age=80,sitetype=3,rl=80)
        self.assertEqual(TreeSpecies.PINE,stand.reference_trees[0].species)
        self.assertEqual(684, futil.overall_stems_per_ha(stand))
        self.assertEqual(83.91228070175438, clearcutting_lim.mean_age_stand(stand))
        self.assertEqual(TreeSpecies.SILVER_BIRCH, futil.solve_dominant_species(stand))
        simulation_aggregates = {
            'operation_results': {},
            'current_time_point': 0,
            'current_operation_tag': 'clearcutting'
        }
        oper_input = (stand, simulation_aggregates)
        (stand_now,aggregates) = clearcut.clearcutting(oper_input, **operation_parameters)
        self.assertEqual(2001, futil.overall_stems_per_ha(stand_now))
        self.assertEqual(79, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['1']['stems_removed_per_ha'])
        self.assertEqual(77, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['3']['stems_removed_per_ha'])
        self.assertEqual(29, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['1']['breast_height_diameter'])
        self.assertEqual(31, aggregates['operation_results']['clearcutting'][0]['clearcut_output']['3']['breast_height_diameter'])
        harvested_trees = aggregates['operation_results']['clearcutting'][0]['clearcut_output']
        volumes, values = cross_cut.cross_cut_thinning_output(harvested_trees)
        self.assertEqual(111.51496563551594,volumes[0][0]*1000)
        vol_total = sum(map(sum,volumes)) #tukki ja kuitu yhteensä
        self.assertEqual(1779.8514844632303, vol_total*1000)
        self.assertEqual(TreeSpecies.SPRUCE,stand.reference_trees[0].species)

    