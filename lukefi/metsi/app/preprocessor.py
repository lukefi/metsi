from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.sim.generators import simple_processable_chain
from lukefi.metsi.sim.runners import evaluate_sequence


def preprocess_stands(stands: StandList, simulation_declaration: dict) -> StandList:
    declared_operations = simulation_declaration.get('preprocessing_operations', {})
    preprocessing_params = simulation_declaration.get('preprocessing_params', {})
    preprocessing_funcs = simple_processable_chain(declared_operations, preprocessing_params)
    stands = evaluate_sequence(stands, *preprocessing_funcs)
    return stands
