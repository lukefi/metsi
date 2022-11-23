from sim.core_types import OpTuple
from forestdatamodel.model import ForestStand
from forestry.utils import get_renewal_costs_as_dict


def cost_only_renewal(payload: OpTuple[ForestStand], **operation_parameters):
    """Renewal operation that does not modify the stand, but only calculates the cost of the given operations"""

    # should there be a check that the operations are inded cost only? so that e.g. planting is not allowed here?
    stand, aggrs = payload
    operations: list = operation_parameters["operations"]
    costs = get_renewal_costs_as_dict(operation_parameters["renewal_cost_table"])

    for op_tag in operations:
        cost_per_ha = costs[op_tag]["cost_per_ha"]
        total_cost = cost_per_ha * stand.area
        aggregate = {aggrs.current_time_point: total_cost}
        aggrs.upsert_nested(aggregate, "renewal", op_tag)

    return payload