from typing import Optional
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.generators import TreatmentFn
from lukefi.metsi.sim.operation_payload import OperationPayload


class MinimumTimeInterval(Condition[ForestStand]):
    def __init__(self, minimum_time: int, operation: Optional[TreatmentFn[ForestStand]] = None) -> None:
        if operation is not None:
            super().__init__(lambda t, x: _check_eligible_to_run(t, x, operation, minimum_time))
        else:
            super().__init__(lambda t, x: _check_eligible_to_run(t, x, self.parent.treatment_fn, minimum_time))


def _get_operation_last_run(operation_history: list[tuple[int, TreatmentFn[ForestStand], dict[str, dict]]],
                            operation_tag: TreatmentFn[ForestStand]) -> Optional[int]:
    return next((t for t, o, _ in reversed(operation_history) if o == operation_tag), None)


def _check_eligible_to_run(
        time_point: int,
        payload: OperationPayload[ForestStand],
        operation: TreatmentFn[ForestStand],
        minimum_time_interval: int) -> bool:
    last_run = _get_operation_last_run(payload.operation_history, operation)
    return last_run is None or minimum_time_interval < (time_point - last_run)
