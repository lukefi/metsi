from app.app_io import Mela2Configuration
from app.export_handlers.j import j_out, parse_j_config
from app.console_logging import print_logline


def export_files(config: Mela2Configuration, decl, data):
    output_handlers = []
    for export_module_declaration in decl:
        format = export_module_declaration.get("format", None)
        if format == "J":
            j_config = parse_j_config(config, export_module_declaration)
            output_handlers.append(lambda: j_out(data, **j_config))
        else:
            print_logline("Unknown output format for export: '{}'".format(format))
    for handler in output_handlers:
        handler()
