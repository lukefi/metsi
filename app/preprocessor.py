from forestry.forestry_types import StandList
from forestry import preprocessing as preprocessing
from sim.generators import simple_processable_chain
from sim.runners import evaluate_sequence


def preprocess_stands(stands: StandList, simulation_declaration: dict) -> StandList:
    preprocessing_operations = simulation_declaration.get('preprocessing_operations', {})
    preprocessing_params = simulation_declaration.get('preprocessing_params', {})
    preprocessing_funcs = simple_processable_chain(preprocessing_operations, preprocessing_params, preprocessing.operation_lookup)
    stands = evaluate_sequence(stands, *preprocessing_funcs)
    return stands
