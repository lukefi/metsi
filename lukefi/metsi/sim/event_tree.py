from typing import Optional
from copy import copy, deepcopy

from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.operation_payload import OperationPayload, ProcessedOperation
from lukefi.metsi.sim.state_tree import StateTree


def identity(x):
    return x


class EventTree[T]:
    """
    Event represents a computational operation in a tree of following event paths.
    """

    __slots__ = ('wrapped_operation', 'branches')

    wrapped_operation: "ProcessedOperation[T]"
    branches: list["EventTree[T]"]

    def __init__(self, operation: Optional["ProcessedOperation[T]"] = None):

        self.wrapped_operation = operation or identity
        self.branches = []

    def operation_chains(self) -> list[list["ProcessedOperation[T]"]]:
        """
        Recursively produce a list of lists of possible operation chains represented by this event tree in post-order
        traversal.
        """
        if len(self.branches) == 0:
            # Yes. A leaf node returns a single chain with a single operation.
            return [[self.wrapped_operation]]
        result: list[list["ProcessedOperation[T]"]] = []
        for branch in self.branches:
            chains = branch.operation_chains()
            for chain in chains:
                result.append([self.wrapped_operation] + chain)
        return result

    def evaluate(self,
                 payload: "OperationPayload[T]",
                 state_tree: Optional[StateTree[PossiblyLayered[T]]] = None) -> list["OperationPayload[T]"]:
        """
        Recursive pre-order walkthrough of this event tree to evaluate its operations with the given payload,
        copying it for branching. If given a root node, a StateTree is also constructed, containing all complete
        intermediate states in the simulation.

        :param payload: the simulation data payload (we don't care what it is here)
        :param state_tree: optional state tree node
        :return: list of result payloads from this EventTree or as concatenated from its branches
        """
        current = self.wrapped_operation(payload)
        branching_state: StateTree | None = None
        if state_tree is not None:
            state_tree.state = deepcopy(current.computational_unit)
            state_tree.done_operation = current.operation_history[-1][1] if len(current.operation_history) > 0 else None
            state_tree.time_point = current.operation_history[-1][0] if len(current.operation_history) > 0 else None
            state_tree.operation_params = current.operation_history[-1][2] if len(
                current.operation_history) > 0 else None

        if len(self.branches) == 0:
            return [current]
        if len(self.branches) == 1:
            if state_tree is not None:
                branching_state = StateTree()
                state_tree.add_branch(branching_state)
            return self.branches[0].evaluate(current, branching_state)
        results: list["OperationPayload[T]"] = []
        for branch in self.branches:
            try:
                if state_tree is not None:
                    branching_state = StateTree()
                evaluated_branch = branch.evaluate(copy(current), branching_state)
                results.extend(evaluated_branch)
                if state_tree is not None and branching_state is not None:
                    state_tree.add_branch(branching_state)
            except UserWarning:
                ...
        if len(results) == 0:
            raise UserWarning("Branch aborted with all children failing")
        return results

    def add_branch(self, et: 'EventTree[T]'):
        self.branches.append(et)
