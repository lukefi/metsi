from typing import Callable, List, Optional, Any


class Step:
    """
    Step represents a computational operation in a tree of alternative computation paths.
    """
    operation: Callable = lambda: None
    branches: List['Step'] = []

    def __init__(self, operation: Callable[[Optional[Any]], Optional[Any]]):
        self.operation = operation

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
        self.branches.append(step)

    def add_branch_from_operation(self, operation: Callable):
        self.add_branch(Step(operation))
