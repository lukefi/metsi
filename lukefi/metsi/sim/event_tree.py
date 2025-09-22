from typing import Optional
from copy import copy, deepcopy

from lukefi.metsi.app.utils import ConditionFailed
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.finalizable import Finalizable
from lukefi.metsi.sim.simulation_payload import SimulationPayload, ProcessedTreatment
from lukefi.metsi.sim.state_tree import StateTree


def identity[T](x: T) -> T:
    return x


class EventTree[T]:
    """
    Event represents a computational operation in a tree of following event paths.
    """

    __slots__ = ('processed_treatment', 'branches')

    processed_treatment: ProcessedTreatment[T]
    branches: list["EventTree[T]"]

    def __init__(self, treatment: Optional[ProcessedTreatment[T]] = None):

        self.processed_treatment = treatment or identity
        self.branches = []

    def operation_chains(self) -> list[list[ProcessedTreatment[T]]]:
        """
        Recursively produce a list of lists of possible operation chains represented by this event tree in post-order
        traversal.
        """
        if len(self.branches) == 0:
            # Yes. A leaf node returns a single chain with a single operation.
            return [[self.processed_treatment]]
        result: list[list[ProcessedTreatment[T]]] = []
        for branch in self.branches:
            chains = branch.operation_chains()
            for chain in chains:
                result.append([self.processed_treatment] + chain)
        return result

    def evaluate(self,
                 payload: SimulationPayload[T],
                 state_tree: Optional[StateTree[PossiblyLayered[T]]] = None) -> list[SimulationPayload[T]]:
        """
        Recursive pre-order walkthrough of this event tree to evaluate its operations with the given payload,
        copying it for branching. If given a root node, a StateTree is also constructed, containing all complete
        intermediate states in the simulation.

        :param payload: the simulation data payload (we don't care what it is here)
        :param state_tree: optional state tree node
        :return: list of result payloads from this EventTree or as concatenated from its branches
        """
        current = self.processed_treatment(payload)
        branching_state: StateTree | None = None
        if state_tree is not None:
            state_tree.state = deepcopy(current.computational_unit)
            state_tree.done_treatment = current.operation_history[-1][1] if len(current.operation_history) > 0 else None
            state_tree.time_point = current.operation_history[-1][0] if len(current.operation_history) > 0 else None
            state_tree.treatment_params = current.operation_history[-1][2] if len(
                current.operation_history) > 0 else None
        if isinstance(current.computational_unit, Finalizable):
            current.computational_unit.finalize()
        if len(self.branches) == 0:
            return [current]
        if len(self.branches) == 1:
            if state_tree is not None:
                branching_state = StateTree()
                state_tree.add_branch(branching_state)
            return self.branches[0].evaluate(current, branching_state)
        results: list[SimulationPayload[T]] = []
        for branch in self.branches:
            try:
                if state_tree is not None:
                    branching_state = StateTree()
                evaluated_branch = branch.evaluate(copy(current), branching_state)
                results.extend(evaluated_branch)
                if state_tree is not None and branching_state is not None:
                    state_tree.add_branch(branching_state)
            except (ConditionFailed, UserWarning):
                ...
        if len(results) == 0:
            raise UserWarning("Branch aborted with all children failing")
        return results

    def add_branch(self, et: 'EventTree[T]'):
        self.branches.append(et)
