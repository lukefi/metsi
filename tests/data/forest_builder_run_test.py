import unittest
from lukefi.metsi.data.formats.ForestBuilder import VMI12Builder, VMI13Builder, ForestCentreBuilder, GeoPackageBuilder
from pathlib import Path


def vmi_file_reader(file: Path) -> list[str]:
    with open(file, 'r', encoding='utf-8') as input_file:
        return input_file.readlines()


def xml_file_reader(file: Path) -> str:
    with open(file, 'r', encoding='utf-8') as input_file:
        return input_file.read()

class TestForestBuilderRun(unittest.TestCase):

    def test_run_smk_forest_builder_build(self):
        assertion = ('SMK_source.xml', 2)
        reference_file = Path('tests', 'data', 'resources', assertion[0])
        list_of_stands = ForestCentreBuilder({"strata_origin": "1", "measured_trees": False},
                                             xml_file_reader(reference_file)).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])


    def test_run_vmi12_forest_builder_build(self):
        assertion = ('VMI12_source_mini.dat', 4)
        reference_file = Path('tests', 'data', 'resources', assertion[0])
        list_of_stands = VMI12Builder({"measured_trees": False, "strata": True}, vmi_file_reader(reference_file)).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])


    def test_run_vmi13_forest_builder_build(self):
        assertion = ('VMI13_source_mini.dat', 3)
        reference_file = Path('tests', 'data', 'resources', assertion[0])
        list_of_stands = VMI13Builder({"measured_trees": False, "strata": True}, vmi_file_reader(reference_file)).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])

    def test_run_smk_geopackage_builder_build(self):
        assertion = (('SMK_source.gpkg', 'geopackage'), 9)
        reference_file = Path('tests', 'data', 'resources', assertion[0][0])
        list_of_stands = GeoPackageBuilder({"strata_origin": "1"},
                                             reference_file).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])