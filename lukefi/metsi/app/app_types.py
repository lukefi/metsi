from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.operation_payload import OperationPayload


ForestOpPayload = OperationPayload[ForestStand]
SimResults = dict[str, list[ForestOpPayload]]
ForestCondition = Condition[ForestOpPayload]

T_co = TypeVar("T_co", covariant=True)


@dataclass
class ExportableContainer(Generic[T_co]):
    """ Output container for application results """
    export_objects: List[T_co]
    additional_vars: Optional[List[str]]
