""" The declarative configuration level of Metsi """
from typing import Any, Dict
from lukefi.metsi.app.file_io import simulation_declaration_from_yaml_file
from examples.declarations.source_data import gpkg_vars, vmi_vars, xml_vars
from examples.declarations.export_prepro import mela, csv_and_json


def read_control(control_yaml: str) -> Dict[str, Any]:
    control_structure = simulation_declaration_from_yaml_file(control_yaml)
    ### ADD YOUR EXTERNAL PYTHON MODULE DECLARATIONS HERE ###
    control_structure['conversions'] = {}
    control_structure['conversions'].update(vmi_vars.vmi_vars)
    # control_structure['conversions'].update(gpkg_vars.gpkg_vars)
    # control_structure['conversions'].update(xml_vars.xml_vars)
    control_structure['export_prepro'] = {}
    control_structure['export_prepro'].update(mela)
    # control_structure['export_preprocessed'].update(csv_and_json)
    return control_structure