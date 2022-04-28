from types import SimpleNamespace
from typing import Callable, List, Optional, Any, OrderedDict, Dict


def identity(x):
    return x


class Step:
    """
    Step represents a computational operation in a tree of alternative computation paths.
    """
    operation: Callable = identity  # default to the identity function, essentially no-op
    branches: List['Step'] = []
    previous: 'Step' or None = None

    def __init__(self, operation: Callable[[Optional[Any]], Optional[Any]] or None = None,
                 previous: 'Step' or None = None):
        self.operation = operation if operation is not None else identity
        self.previous = previous
        self.branches = []

    def find_root(self: 'Step'):
        return self if self.previous is None else self.previous.find_root()

    def attach(self, previous: 'Step'):
        self.previous = previous
        previous.add_branch(self)

    def operation_chains(self):
        """
        Recursively produce a list of lists of possible operation chains represented by this tree in post-order
        traversal.
        """
        if len(self.branches) == 0:
            # Yes. A leaf node returns a single chain with a single operation.
            return [[self.operation]]
        else:
            result = []
            for branch in self.branches:
                chains = branch.operation_chains()
                for chain in chains:
                    result.append([self.operation] + chain)
            return result

    def add_branch(self, step: 'Step'):
        step.previous = self
        self.branches.append(step)

    def add_branch_from_operation(self, operation: Callable):
        self.add_branch(Step(operation, self))


class SimulationParams(SimpleNamespace):
    """Control parameter set for simulation time progressing"""
    initial_step_time: int
    step_time_interval: int
    final_step_time: int

    def simulation_time_series(self) -> range:
        return range(
            self.initial_step_time,
            self.final_step_time + 1,
            self.step_time_interval
        )


class OperationPayload(SimpleNamespace):
    """Data structure for keeping simulation state and progress data. Passed on as the data package of chained
    operation calls. """
    simulation_state: Any
    run_history: dict or None
    aggregated_results: Dict[str, OrderedDict[int, Any]]
