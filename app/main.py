import forestry.operations
from sim.core_types import OperationPayload
from sim.runners import run_chains_iteratively
from sim.generators import compose, full_tree_generators_from_declaration
from app.file_io import forest_stands_from_json_file, simulation_declaration_from_yaml_file

if __name__ == "__main__":
    # TODO: use argparse
    stands = forest_stands_from_json_file('vmi12_weibull_trees.json')
    simulation_declaration = simulation_declaration_from_yaml_file('control.yaml')

    generators = full_tree_generators_from_declaration(simulation_declaration, forestry.operations.operation_lookup)
    tree = compose(*generators)

    for stand in stands:
        print("Running simulation for stand {}".format(stand.identifier))
        payload = OperationPayload(
            simulation_state=stand,
            run_history={}
        )
        chains = tree.operation_chains()
        result = run_chains_iteratively(payload, chains)
        print("Obtained {} variants for stand {}\n".format(len(result), stand.identifier))
