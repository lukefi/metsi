import os
import sys

from forestdatamodel.model import ForestStand

from app.app_io import parse_cli_arguments, Mela2Configuration, generate_program_configuration, RunMode
from app.file_io import simulation_declaration_from_yaml_file, prepare_target_directory
from sim.core_types import OperationPayload


def preprocess(config: Mela2Configuration, control: dict) -> list[ForestStand]:
    print("Preprocessing...")
    return []


def simulate(config: Mela2Configuration, control: dict) -> dict[str, list[OperationPayload]]:
    print("Simulating...")
    return {}


def post_process(config: Mela2Configuration, control: dict) -> dict[str, list[OperationPayload]]:
    print("Post processing...")
    return {}


def export(control: dict) -> None:
    print("Exporting...")


mode_runners = {
    RunMode.PREPROCESS: preprocess,
    RunMode.SIMULATE: simulate,
    RunMode.POSTPROCESS: post_process,
    RunMode.EXPORT: export
}


def main() -> int:
    cli_arguments = parse_cli_arguments(sys.argv[1:])
    control_file = Mela2Configuration.control_file if cli_arguments.control_file is None else cli_arguments.control_file
    try:
        control_structure = simulation_declaration_from_yaml_file(control_file)
    except IOError:
        print(f"Application control file path '{control_file}' can not be read. Aborting....")
        return 1
    try:
        app_config = generate_program_configuration(cli_arguments, control_structure['app_configuration'])
    except Exception as e:
        print(e)
        print("Aborting run...")
        return 1

    for mode in app_config.run_modes:
        mode_runners[mode](app_config, control_structure)

    return 0


if __name__ == '__main__':
    code = main()
    sys.exit(code)
