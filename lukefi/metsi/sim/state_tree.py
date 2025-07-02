from collections.abc import Callable
from typing import Any, Optional


class StateTree[T]:
    state: T
    done_operation: Optional[Callable[[tuple[T, Any]], tuple[T, Any]]]
    operation_params: Optional[dict[str, Any]]
    time_point: Optional[int]
    branches: list['StateTree[T]']

    def __init__(self):
        self.branches = []

    def add_branch(self, branch: 'StateTree[T]'):
        self.branches.append(branch)
