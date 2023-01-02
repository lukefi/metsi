from pathlib import Path

from lukefi.metsi.app.app_io import Mela2Configuration
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.app.export_handlers.j import j_out, parse_j_config
from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.app.export_handlers.rm_timber import rm_schedules_events_timber, rm_schedules_events_trees


def export_files(config: Mela2Configuration, decl: list[dict], data: SimResults):
    output_handlers = []
    for export_module_declaration in decl:
        export_module = export_module_declaration.get("format", None)
        if export_module == "J":
            j_config = parse_j_config(config, export_module_declaration)
            output_handlers.append((export_module,
                                    lambda: j_out(data, **j_config)))
        elif export_module == "rm_schedules_events_timber":
            filename1 = export_module_declaration.get("filename", "rm_schedule_timber_year_sums.txt")
            target_path1 = Path(config.target_directory, filename1)
            output_handlers.append((export_module,
                                    lambda: rm_schedules_events_timber(target_path1, data)))
        elif export_module == "rm_schedules_events_trees":
            filename2 = export_module_declaration.get("filename", "rm_schedule_trees.txt")
            target_path2 = Path(config.target_directory, filename2)
            output_handlers.append((export_module,
                                    lambda: rm_schedules_events_trees(target_path2, data)))
        else:
            print_logline(f"Unknown output format for export: '{export_module}'")
    for export_module, handler in output_handlers:
        print_logline(f"Exporting {export_module}...")
        handler()
