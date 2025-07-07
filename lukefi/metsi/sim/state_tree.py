from collections.abc import Callable
from pathlib import Path
import pickle
from typing import Any, Optional

from lukefi.metsi.app.utils import MetsiException


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

    def save_to_file(self, path: str | Path, fmt: str = "pickle"):
        if fmt == "pickle":
            with open(path, "wb") as f:
                pickle.dump(self, f)
        else:
            raise MetsiException(f"Unsupported format {fmt}")

    @classmethod
    def read_from_file(cls, path: str | Path, fmt: str = "pickle") -> 'StateTree':
        if fmt == "pickle":
            with open(path, "rb") as f:
                return pickle.load(f)
        raise MetsiException(f"Unable to load {path} as {fmt}")
