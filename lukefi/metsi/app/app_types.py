from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.core_types import OperationPayload

ForestOpPayload = OperationPayload[ForestStand]
SimResults = dict[str, list[ForestOpPayload]]
