from forestdatamodel.model import ForestStand

from forestry.utils.collectives import property_collector, autocollective, _collector_wrapper
from sim.core_types import OpTuple
from sim.operations import T


def report_collectives(input: OpTuple[T], /, **collectives: str) -> OpTuple[T]:
    state, aggr = input
    res = _collector_wrapper(
        collectives,
        lambda name: autocollective(getattr(state, name)),
        lambda name: autocollective(aggr.operation_results[name]),
        state = state,
        aggr = aggr.operation_results,
        time = aggr.current_time_point
    )
    aggr.store('report_collectives', res)
    return input


def report_state(input: OpTuple[T], /, **operation_parameters: str) -> OpTuple[T]:
    state, aggr = input
    res = _collector_wrapper(
        operation_parameters,
        lambda name: autocollective(getattr(state, name)),
        lambda name: autocollective(
            aggr.operation_results[name],
            time_point=[aggr.current_time_point]),
        state=state
    )
    aggr.store('report_state', res)
    return input


def collect_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, aggr = input
    output_name = operation_parameters.get('output_name', 'collect_properties')
    result_rows = []
    if not len(operation_parameters):
        return input
    for key, properties in operation_parameters.items():
        objects: list[object]
        if isinstance(properties, str):
            properties = [properties]
        elif not isinstance(properties, list):
            raise Exception(f"Properties to collect must be a list of strings or a single string for {key}")
        if key == "stand":
            objects = [stand]
        elif key == "tree":
            objects = stand.reference_trees
        elif key == "stratum":
            objects = stand.tree_strata
        else:
            objects = list(filter(lambda obj: obj.time_point == aggr.current_time_point, aggr.get_list_result(key)))
        collected = property_collector(objects, properties)
        result_rows.extend(collected)
    aggr.store(output_name, result_rows)
    return stand, aggr


def collect_standing_tree_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    properties = operation_parameters.get("properties")
    return collect_properties(input, tree=properties, output_name="collect_standing_tree_properties")


def collect_felled_tree_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    properties = operation_parameters.get("properties")
    return collect_properties(input, felled_trees=properties, output_name="collect_felled_tree_properties")


def report_period(input: OpTuple[T], /, **operation_parameters: str) -> OpTuple[T]:
    _, aggr = input
    last_period = aggr.prev('report_period')
    t0 = aggr.initial_time_point if last_period is None else list(aggr.get('report_period').keys())[-1]
    res = _collector_wrapper(
        operation_parameters,
        lambda name: autocollective(
            aggr.operation_results[name],
            time_point=range(t0, aggr.current_time_point)
        )
    )
    aggr.store('report_period', res)
    return input
