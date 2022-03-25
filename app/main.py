import sys
import forestry.operations
from sim.core_types import OperationPayload
from sim.runners import run_chains_iteratively
from sim.generators import compose, generators_from_declaration
from app.file_io import forest_stands_from_json_file, simulation_declaration_from_yaml_file
from app.app_io import parse_cli_arguments

if __name__ == "__main__":
    # TODO: use argparse
    app_arguments = parse_cli_arguments(sys.argv[1:])
    print("app_arguments: ", app_arguments)
    stands = forest_stands_from_json_file(app_arguments.domain_state_file)
    simulation_declaration = simulation_declaration_from_yaml_file(app_arguments.control_file)

    generators = generators_from_declaration(simulation_declaration, forestry.operations.operation_lookup)
    tree = compose(*generators)

    payload = OperationPayload(
        simulation_state=stands[1],
        run_history = {}
    )

    chains = tree.operation_chains()

    run_chains_iteratively(payload, chains)
