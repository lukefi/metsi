from pathlib import Path

from app.app_io import Mela2Configuration
from app.app_types import SimResults
from app.export_handlers.j import j_out, parse_j_config
from app.console_logging import print_logline
from app.export_handlers.rm_timber import rm_schedules_events_timber


def export_files(config: Mela2Configuration, decl: list[dict], data: SimResults):
    output_handlers = []
    for export_module_declaration in decl:
        format = export_module_declaration.get("format", None)
        if format == "J":
            j_config = parse_j_config(config, export_module_declaration)
            output_handlers.append(lambda: j_out(data, **j_config))
        elif format == "rm_schedules_events_timber":
            output_handlers.append(lambda: rm_schedules_events_timber(Path(config.target_directory, export_module_declaration.get("filename", "rm_schedule_timber_year_sums.txt")), data))
        else:
            print_logline("Unknown output format for export: '{}'".format(format))
    for handler in output_handlers:
        handler()
