from app.app_io import Mela2Configuration
from app.app_types import SimResults
from forestry.post_ops import operation_lookup
from sim.core_types import OperationPayload
from sim.generators import simple_processable_chain
from sim.runners import evaluate_sequence


def post_process_alternatives(config: Mela2Configuration, control: dict, input_data: SimResults):
    chain = simple_processable_chain(
        control.get('post_processing', []),
        control.get('operation_params', {}),
        operation_lookup
    )
    result = {}
    for identifier, schedules in input_data.items():
        result[identifier] = []
        for schedule in schedules:
            payload = (schedule.computational_unit, schedule.collected_data)
            processed_schedule = evaluate_sequence(payload, *chain)
            result[identifier].append(
                OperationPayload(
                    computational_unit=processed_schedule[0],
                    collected_data=processed_schedule[1]))
    return result
