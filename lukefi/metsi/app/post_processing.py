from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.sim.generators import simple_processable_chain
from lukefi.metsi.sim.operation_payload import OperationPayload
from lukefi.metsi.sim.runners import evaluate_sequence


def post_process_alternatives(config: MetsiConfiguration, control: dict, input_data: SimResults):
    _ = config
    chain = simple_processable_chain(
        control.get('post_processing', []),
        control.get('operation_params', {})
    )
    result: dict[str, list[OperationPayload]] = {}
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
