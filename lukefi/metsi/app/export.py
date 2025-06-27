import copy
from pathlib import Path
from functools import partial
from typing import Callable


from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.app_types import SimResults, ExportableContainer
from lukefi.metsi.app.export_handlers.j import j_out, parse_j_config
from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.app.export_handlers.rm_timber import rm_schedules_events_timber, rm_schedules_events_trees
from lukefi.metsi.app.file_io import write_stands_to_file, determine_file_path
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.sim.generators import simple_processable_chain
from lukefi.metsi.sim.runners import evaluate_sequence


def export_files(config: MetsiConfiguration, decl: list[dict], data: SimResults):
    output_handlers: list[tuple[str, Callable[[], None]]] = []
    for export_module_declaration in decl:
        export_module = export_module_declaration.get("format", None)
        if export_module == "J":
            j_config = parse_j_config(config, export_module_declaration)
            output_handlers.append((export_module, partial(j_out, data, **j_config)))
        elif export_module == "rm_schedules_events_timber":
            filename1 = export_module_declaration.get("filename", "rm_schedule_timber_year_sums.txt")
            target_path1 = Path(config.target_directory, filename1)
            output_handlers.append((export_module, partial(rm_schedules_events_timber,target_path1, data)))
        elif export_module == "rm_schedules_events_trees":
            filename2 = export_module_declaration.get("filename", "rm_schedule_trees.txt")
            target_path2 = Path(config.target_directory, filename2)
            output_handlers.append((export_module, partial(rm_schedules_events_trees, target_path2, data)))
        else:
            print_logline(f"Unknown output format for export: '{export_module}'")
    for export_module, handler in output_handlers:
        print_logline(f"Exporting {export_module}...")
        handler()

def export_preprocessed(target_directory: str, decl: dict, stands: StandList) -> None:
    output_formats = list(decl.keys())
    print_logline(f"Writing all preprocessed data to directory '{target_directory}'")
    for output_format in output_formats:
        operations = decl[output_format].get('operations', None)
        operation_params = decl[output_format].get('operation_params', None)
        additional_varnames = decl[output_format].get('additional_variables', None)
        file_name = f"preprocessing_result.{output_format}"
        filepaths = determine_file_path(target_directory, file_name)
        if operations is not None:
            operation_chain = simple_processable_chain(operations,
                                                       operation_params)
            modified_stands = evaluate_sequence(
                copy.deepcopy(stands),
                *operation_chain)
            result = ExportableContainer(modified_stands, additional_varnames)
        else:
            result = ExportableContainer(stands, additional_varnames)
        print_logline(f"Writing preprocessed data to '{target_directory}\{file_name}'")
        write_stands_to_file(result, filepaths, output_format)
