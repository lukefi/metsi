from lukefi.metsi.data.model import ForestStand

from lukefi.metsi.domain.utils.collectives import property_collector, autocollective, _collector_wrapper
from lukefi.metsi.sim.core_types import OpTuple
from lukefi.metsi.sim.operations import T


def report_collectives(input: OpTuple[T], /, **collectives: str) -> OpTuple[T]:
    state, collected_data = input
    res = _collector_wrapper(
        collectives,
        lambda name: autocollective(getattr(state, name)),
        lambda name: autocollective(collected_data.operation_results[name]),
        state = state,
        collected_data = collected_data.operation_results,
        time = collected_data.current_time_point
    )
    collected_data.store('report_collectives', res)
    return input


def report_state(input: OpTuple[T], /, **operation_parameters: str) -> OpTuple[T]:
    state, collected_data = input
    res = _collector_wrapper(
        operation_parameters,
        lambda name: autocollective(getattr(state, name)),
        lambda name: autocollective(
            collected_data.operation_results[name],
            time_point=[collected_data.current_time_point]),
        state=state
    )
    collected_data.store('report_state', res)
    return input


def collect_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    stand, collected_data = input
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
            objects = list(filter(lambda obj: obj.time_point == collected_data.current_time_point, collected_data.get_list_result(key)))
        collected = property_collector(objects, properties)
        result_rows.extend(collected)
    collected_data.store(output_name, result_rows)
    return stand, collected_data


def collect_standing_tree_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    properties = operation_parameters.get("properties")
    return collect_properties(input, tree=properties, output_name="collect_standing_tree_properties")


def collect_felled_tree_properties(input: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    properties = operation_parameters.get("properties")
    return collect_properties(input, felled_trees=properties, output_name="collect_felled_tree_properties")


def report_period(input: OpTuple[T], /, **operation_parameters: str) -> OpTuple[T]:
    _, collected_data = input
    last_period = collected_data.prev('report_period')
    t0 = collected_data.initial_time_point if last_period is None else list(collected_data.get('report_period').keys())[-1]
    res = _collector_wrapper(
        operation_parameters,
        lambda name: autocollective(
            collected_data.operation_results[name],
            time_point=range(t0, collected_data.current_time_point)
        )
    )
    collected_data.store('report_period', res)
    return input
