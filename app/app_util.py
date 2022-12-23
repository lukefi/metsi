from forestdatamodel.model import ForestStand

from app.app_types import ForestOperation
from sim.core_types import OpTuple


def create_checked_operations_lookup(operation_lookup: dict[str, ForestOperation]) -> dict[str, ForestOperation]:
    retval = {}
    for k, v in operation_lookup.items():
        retval[k] = lambda data, **params: checked_forest_operation(k, v, data, **params)
    return retval




def checked_forest_operation(tag: str, op: ForestOperation, data: OpTuple[ForestStand], **operation_params) -> ForestOperation:
    state, _ = data
    try:
        op(data, **operation_params)
    except Exception as e:
        # TODO: When migrating to Python 3.11, BaseException.add_note(note) allows including extra message natively
        e.__dict__['extra'] = f"operation '{tag}' failed with unit '{state.identifier}'"
        raise e
