from typing import TYPE_CHECKING
from lukefi.metsi.app.utils import ConditionFailed
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.simulation_payload import SimulationPayload
if TYPE_CHECKING:
    from lukefi.metsi.sim.generators import TreatmentFn


def processor[T](payload: SimulationPayload[T],
                 operation: "TreatmentFn[T]",
                 operation_tag: "TreatmentFn[T]",
                 time_point: int,
                 preconditions: list[Condition[SimulationPayload[T]]],
                 postconditions: list[Condition[SimulationPayload[T]]],
                 **operation_parameters: dict[str, dict]) -> SimulationPayload[T]:
    """Managed run conditions and history of a simulator operation. Evaluates the operation."""
    for condition in preconditions:
        if not condition(time_point, payload):
            raise ConditionFailed(f'{operation_tag} aborted - condition "{condition}" failed')

    payload.collected_data.current_time_point = time_point
    try:
        new_state, new_collected_data = operation((payload.computational_unit, payload.collected_data))
    except UserWarning as e:
        raise UserWarning(f"Unable to perform operation {operation_tag}, "
                          f"at time point {time_point}; reason: {e}") from e

    newpayload: SimulationPayload[T] = SimulationPayload(
        computational_unit=new_state,
        collected_data=payload.collected_data if new_collected_data is None else new_collected_data,
        operation_history=payload.operation_history
    )

    for condition in postconditions:
        if not condition(time_point, newpayload):
            raise ConditionFailed(f'{operation_tag} aborted - condition "{condition}" failed')

    payload.operation_history.append((time_point, operation_tag, operation_parameters))

    return newpayload
