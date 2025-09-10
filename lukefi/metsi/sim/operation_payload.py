from collections.abc import Callable
from copy import copy, deepcopy
from types import SimpleNamespace
from typing import TYPE_CHECKING, TypeVar

from lukefi.metsi.data.layered_model import LayeredObject, PossiblyLayered
from lukefi.metsi.sim.collected_data import CollectedData
if TYPE_CHECKING:
    from lukefi.metsi.sim.generators import TreatmentFn


class OperationPayload[T](SimpleNamespace):
    """Data structure for keeping simulation state and progress data. Passed on as the data package of chained
    operation calls. """
    computational_unit: PossiblyLayered[T]
    collected_data: CollectedData
    operation_history: list[tuple[int, "TreatmentFn[T]", dict[str, dict]]]

    def __copy__(self) -> "OperationPayload[T]":
        copy_like: PossiblyLayered[T]
        if isinstance(self.computational_unit, LayeredObject):
            copy_like = self.computational_unit.new_layer()
            copy_like.reference_trees = [tree.new_layer() for tree in copy_like.reference_trees]
            copy_like.tree_strata = [stratum.new_layer() for stratum in copy_like.tree_strata]
        else:
            copy_like = deepcopy(self.computational_unit)

        return OperationPayload(
            computational_unit=copy_like,
            collected_data=copy(self.collected_data),
            operation_history=list(self.operation_history)
        )

T = TypeVar("T")
ProcessedOperation = Callable[[OperationPayload[T]], OperationPayload[T]]
