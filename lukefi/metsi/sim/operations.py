from typing import TYPE_CHECKING, Callable, Optional, TypeVar

from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.operation_payload import ProcessedOperation
from lukefi.metsi.sim.operation_payload import OperationPayload
if TYPE_CHECKING:
    from lukefi.metsi.sim.generators import TreatmentFn


T = TypeVar("T")


def _get_operation_last_run(operation_history: list[tuple[int, "TreatmentFn[T]", dict[str, dict]]],
                            operation_tag: "TreatmentFn[T]") -> Optional[int]:
    return next((t for t, o, _ in reversed(operation_history) if o == operation_tag), None)


def do_nothing(data: T, **kwargs) -> T:
    _ = kwargs
    return data


def prepared_operation(operation_entrypoint: Callable[[T], T], **operation_parameters) -> Callable[[T], T]:
    """prepares an opertion entrypoint function with configuration parameters"""
    return lambda state: operation_entrypoint(state, **operation_parameters)


def prepared_processor(operation_tag: "TreatmentFn[T]",
                       time_point: int,
                       operation_conditions: list[Condition[T]],
                       **operation_parameters: dict[str,
                                                    dict]) -> ProcessedOperation[T]:
    """prepares a processor function with an operation entrypoint"""
    operation: "TreatmentFn[T]" = prepared_operation(operation_tag, **operation_parameters)
    return lambda payload: _processor(payload, operation, operation_tag, time_point,
                                      operation_conditions, **operation_parameters)


def _processor(payload: OperationPayload[T], operation: "TreatmentFn[T]", operation_tag: "TreatmentFn[T]",
               time_point: int, operation_conditions: list[Condition[T]],
               **operation_parameters: dict[str, dict]) -> OperationPayload[T]:
    """Managed run conditions and history of a simulator operation. Evaluates the operation."""
    for condition in operation_conditions:
        if not condition(time_point, payload):
            raise UserWarning(f'{operation_tag} aborted - condition "{condition}" failed')

    payload.collected_data.current_time_point = time_point
    try:
        new_state, new_collected_data = operation((payload.computational_unit, payload.collected_data))
    except UserWarning as e:
        raise UserWarning(f"Unable to perform operation {operation_tag}, "
                          f"at time point {time_point}; reason: {e}") from e

    payload.operation_history.append((time_point, operation_tag, operation_parameters))

    newpayload: OperationPayload[T] = OperationPayload(
        computational_unit=new_state,
        collected_data=payload.collected_data if new_collected_data is None else new_collected_data,
        operation_history=payload.operation_history
    )
    return newpayload
