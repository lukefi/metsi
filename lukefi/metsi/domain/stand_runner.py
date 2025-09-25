from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.data.layered_model import LayeredObject, PossiblyLayered
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.domain.forestry_types import ForestOpPayload, StandList
from lukefi.metsi.sim.collected_data import CollectedData
from lukefi.metsi.sim.runners import Evaluator, TreeRunner
from lukefi.metsi.sim.sim_configuration import SimConfiguration


def run_stands(stands: StandList,
               config: SimConfiguration[ForestStand],
               formation_strategy: TreeRunner[ForestStand],
               evaluation_strategy: Evaluator[ForestStand]) -> dict[str, list[ForestOpPayload]]:
    """Run the simulation for all given stands, from the given declaration, using the given runner. Return the
    results organized into a dict keyed with stand identifiers."""

    retval: dict[str, list[ForestOpPayload]] = {}
    for stand in stands:
        overlaid_stand: PossiblyLayered[ForestStand]
        if stand.reference_trees_soa is None or stand.tree_strata_soa is None:
            # If the state is not vectorized, wrap it as a LayeredObject so that new nodes in the EventTree don't have
            # to copy the entire state in memory and can just store the data that has actually changed instead.
            # This is not necessary for vectorized data since similar functionality is provided by the finalize method.
            overlaid_stand = LayeredObject[ForestStand](stand)
            overlaid_stand.reference_trees = [LayeredObject[ReferenceTree]
                                              (tree) for tree in overlaid_stand.reference_trees]
            overlaid_stand.tree_strata = [LayeredObject[TreeStratum](stratum) for stratum in overlaid_stand.tree_strata]
        else:
            overlaid_stand = stand

        payload = ForestOpPayload(
            computational_unit=overlaid_stand,
            collected_data=CollectedData(initial_time_point=config.time_points[0]),
            operation_history=[],
        )

        schedule_payloads = formation_strategy(payload, config, evaluation_strategy)
        identifier = stand.identifier
        print_logline(f"Alternatives for stand {identifier}: {len(schedule_payloads)}")
        retval[identifier] = schedule_payloads
    return retval
