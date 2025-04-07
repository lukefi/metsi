import unittest
from lukefi.metsi.data.formats.ForestBuilder import VMI12Builder, VMI13Builder, XMLBuilder, GeoPackageBuilder
from pathlib import Path
from lukefi.metsi.app.enum import StrataOrigin


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
        list_of_stands = XMLBuilder(
            builder_flags={"strata_origin": StrataOrigin.INVENTORY, "measured_trees": False},
            declared_conversions={},
            data=xml_file_reader(reference_file)).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])


    def test_run_vmi12_forest_builder_build(self):
        assertion = ('VMI12_source_mini.dat', 4)
        reference_file = Path('tests', 'data', 'resources', assertion[0])
        list_of_stands = VMI12Builder(
            builder_flags={"measured_trees": False, "strata": True},
             declared_conversions={},
             data_rows=vmi_file_reader(reference_file)).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])


    def test_run_vmi13_forest_builder_build(self):
        assertion = ('VMI13_source_mini.dat', 4)
        reference_file = Path('tests', 'data', 'resources', assertion[0])
        list_of_stands = VMI13Builder(
            builder_flags={"measured_trees": False, "strata": True},
            declared_conversions={},
            data_rows=vmi_file_reader(reference_file)).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])

    def test_run_smk_geopackage_builder_build(self):
        assertion = (('SMK_source.gpkg', 'geopackage'), 9)
        reference_file = Path('tests', 'data', 'resources', assertion[0][0])
        list_of_stands = GeoPackageBuilder(
            builder_flags={"strata_origin": StrataOrigin.INVENTORY},
            declared_conversions={},
            db_path=reference_file).build()
        result = len(list_of_stands)
        self.assertEqual(result, assertion[1])