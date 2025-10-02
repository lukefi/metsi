from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.domain.forestry_types import SimResults
from lukefi.metsi.sim.operations import simple_processable_chain
from lukefi.metsi.sim.simulation_payload import SimulationPayload
from lukefi.metsi.sim.runners import evaluate_sequence


def post_process_alternatives(config: MetsiConfiguration, control: dict, input_data: SimResults):
    _ = config
    chain = simple_processable_chain(
        control.get('post_processing', []),
        control.get('operation_params', {})
    )
    result: dict[str, list[SimulationPayload]] = {}
    for identifier, schedules in input_data.items():
        result[identifier] = []
        for schedule in schedules:
            payload = (schedule.computational_unit, schedule.collected_data)
            processed_schedule = evaluate_sequence(payload, *chain)
            result[identifier].append(
                SimulationPayload(
                    computational_unit=processed_schedule[0],
                    collected_data=processed_schedule[1]))
    return result
