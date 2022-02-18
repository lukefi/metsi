import forestry.operations
from sim.core_types import OperationPayload
from sim.runners import run_chains_iteratively
from sim.generators import compose, generators_from_declaration
from app.file_io import forest_stands_from_json_file, simulation_declaration_from_yaml_file

if __name__ == "__main__":
    # TODO: use argparse
    stands = forest_stands_from_json_file('input.json')
    simulation_declaration = simulation_declaration_from_yaml_file('control.yaml')

    generators = generators_from_declaration(simulation_declaration, forestry.operations.operation_lookup)
    tree = compose(*generators)

    payload = OperationPayload(
        simulation_state=stands[1]
    )

    chains = tree.operation_chains()

    run_chains_iteratively(payload, chains)
