from typing import Optional
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.generators import TreatmentFn
from lukefi.metsi.sim.simulation_payload import SimulationPayload


class MinimumTimeInterval[T](Condition[SimulationPayload[T]]):
    def __init__(self, minimum_time: int, treatment: TreatmentFn[T]) -> None:
        super().__init__(lambda t, x: _check_eligible_to_run(t, x, treatment, minimum_time))


def _get_operation_last_run[T](operation_history: list[tuple[int, TreatmentFn[T], dict[str, dict]]],
                               operation_tag: TreatmentFn[T]) -> Optional[int]:
    return next((t for t, o, _ in reversed(operation_history) if o == operation_tag), None)


def _check_eligible_to_run[T](
        time_point: int,
        payload: SimulationPayload[T],
        treatment: TreatmentFn[T],
        minimum_time_interval: int) -> bool:
    last_run = _get_operation_last_run(payload.operation_history, treatment)
    return last_run is None or minimum_time_interval <= (time_point - last_run)
