from collections.abc import Callable
from typing import Any


class StateTree[T]:
    state: T
    done_operation: Callable[[tuple[T, Any]], tuple[T, Any]]
    operation_params: dict[str, Any]
    time_point: int
    branches: list['StateTree[T]']

    def __init__(self, state: T, operation: Callable[[tuple[T, Any]],
                 tuple[T, Any]], time_point: int, parameters: dict[str, Any]):
        self.state = state
        self.done_operation = operation
        self.operation_params = parameters
        self.time_point = time_point
        self.branches = []

    def add_branch(self, branch: 'StateTree[T]'):
        self.branches.append(branch)
