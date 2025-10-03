from collections.abc import Callable
from copy import copy, deepcopy
from types import SimpleNamespace
from typing import TYPE_CHECKING, TypeVar

from lukefi.metsi.data.layered_model import LayeredObject, PossiblyLayered
from lukefi.metsi.sim.collected_data import CollectedData
if TYPE_CHECKING:
    from lukefi.metsi.sim.generators import TreatmentFn


class SimulationPayload[T](SimpleNamespace):
    """Data structure for keeping simulation state and progress data. Passed on as the data package of chained
    operation calls. """
    computational_unit: PossiblyLayered[T]
    collected_data: CollectedData
    operation_history: list[tuple[int, "TreatmentFn[T]", dict[str, dict]]]

    def __copy__(self) -> "SimulationPayload[T]":
        copy_like: PossiblyLayered[T]
        if isinstance(self.computational_unit, LayeredObject):
            copy_like = self.computational_unit.new_layer()
        else:
            copy_like = deepcopy(self.computational_unit)

        return SimulationPayload(
            computational_unit=copy_like,
            collected_data=copy(self.collected_data),
            operation_history=list(self.operation_history)
        )

T = TypeVar("T")
ProcessedTreatment = Callable[[SimulationPayload[T]], SimulationPayload[T]]
