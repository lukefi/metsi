from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.core_types import OperationPayload
from dataclasses import dataclass
from typing import Generic, TypeVar, List

T = TypeVar("T")

ForestOpPayload = OperationPayload[ForestStand]
SimResults = dict[str, list[ForestOpPayload]]

@dataclass
class ExportableContainer(Generic[T]):
    """ Output container for application results """
    export_objects: List[T]
    additional_vars: List[str]
