from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.sim.condition import Condition
from lukefi.metsi.sim.simulation_payload import SimulationPayload

StandList = list[ForestStand]
ForestOpPayload = SimulationPayload[ForestStand]
SimResults = dict[str, list[ForestOpPayload]]
ForestCondition = Condition[ForestOpPayload]
