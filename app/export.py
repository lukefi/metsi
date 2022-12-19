from pathlib import Path

from app.app_io import Mela2Configuration
from app.app_types import SimResults
from app.export_handlers.j import j_out, parse_j_config
from app.console_logging import print_logline
from app.export_handlers.rm_timber import rm_schedules_events_timber, rm_schedules_events_trees


def export_files(config: Mela2Configuration, decl: list[dict], data: SimResults):
    output_handlers = []
    for export_module_declaration in decl:
        export_module = export_module_declaration.get("format", None)
        if export_module == "J":
            j_config = parse_j_config(config, export_module_declaration)
            output_handlers.append((export_module,
                                    lambda: j_out(data, **j_config)))
        elif export_module == "rm_schedules_events_timber":
            filename = export_module_declaration.get("filename", "rm_schedule_timber_year_sums.txt")
            target_path = Path(config.target_directory, filename)
            output_handlers.append((export_module,
                                    lambda: rm_schedules_events_timber(target_path, data)))
        elif export_module == "rm_schedules_events_trees":
            filename = export_module_declaration.get("filename", "rm_schedule_trees.txt")
            target_path = Path(config.target_directory, filename)
            output_handlers.append((export_module,
                                    lambda: rm_schedules_events_trees(target_path, data)))
        else:
            print_logline("Unknown output format for export: '{}'".format(export_module))
    for export_module, handler in output_handlers:
        print_logline(f"Exporting {export_module}...")
        handler()
