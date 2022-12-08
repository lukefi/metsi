from forestdatamodel.model import ForestStand
from sim.core_types import OperationPayload

ForestOpPayload = OperationPayload[ForestStand]
SimResults = dict[str, list[ForestOpPayload]]
