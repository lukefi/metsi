from dataclasses import dataclass
from typing import List, Optional
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.core_types import OperationPayload


ForestOpPayload = OperationPayload[ForestStand]
SimResults = dict[str, list[ForestOpPayload]]


@dataclass
class ExportableContainer[T]:
    """ Output container for application results """
    export_objects: List[T]
    additional_vars: Optional[List[str]]
