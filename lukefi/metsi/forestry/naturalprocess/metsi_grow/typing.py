from types import GenericAlias
from typing import Any, Optional, Sequence, Type, TypeVar, Union
import numpy as np
import numpy.typing as npt

# kinda hacky but good enough for now
Reals = Union[Sequence[float], npt.NDArray, npt.NDArray[np.float64]]
Ints  = Union[Sequence[int], npt.NDArray, npt.NDArray[np.int32], npt.NDArray[np.int64]]

# this only exists so that type hints get passed to documentation
T = TypeVar("T")
def update_wrapper_generic(wrapper: T, wrapped: Any, generic: Optional[Type] = None) -> T:
    wrapper.__doc__ = wrapped.__doc__
    wrapper.__annotations__ = dict(wrapped.__annotations__)
    if generic and "return" in wrapper.__annotations__:
        wrapper.__annotations__["return"] = GenericAlias(generic, wrapper.__annotations__["return"])
    return wrapper
