import builtins
from functools import lru_cache
from typing import Any, Callable, Iterator, Optional
import numpy as np

GetVarFn = Callable[[str], Any]
CollectFn = Callable[[Any], Any]

#---- collector functions ----------------------------------------

# only reason this inherits dict is because the global namespace for eval() must be a dict.
class Globals(dict):

    __slots__ = "delegate",

    def __init__(self):
        self.delegate: Optional[GetVarFn] = None

    def __missing__(self, name: str) -> Any:
        return self.delegate(name) # type: ignore -- this shouldn't be called before delegate is set


@lru_cache
def compile(expr: str) -> CollectFn:
    """Compile a Python expression `expr` into a collector function."""
    globals = Globals()
    e = eval(f"lambda: {expr}", globals)
    def fn(getvar: GetVarFn) -> Any:
        globals.delegate = getvar
        ret = e()
        if hasattr(ret, "__collect__"):
            ret = ret.__collect__()
        return ret
    return fn


def collect_all(collectives: dict[str, str], getvar: GetVarFn) -> dict[str, Any]:
    """Collect variables from a state defined by `getvar`."""
    return {k: compile(v)(getvar) for k,v in collectives.items()}


def getvarfn(*xs: Any, **named: Any) -> GetVarFn:
    """Helper for composing a `getvar` function.
    - if an object is callable, it's used as-is,
    - if an object has __getitem__, it's checked,
    - otherwise getattr() is used,
    - first parameter goes first and so on.
    - any `KeyError` or `AttributeError` moves to the next object."""
    if named:
        xs = [named, *xs] # type: ignore
    xs = [*xs, builtins] # type: ignore
    def getvar(name: str) -> Any:
        for x in xs:
            try:
                if callable(x):
                    return x(name)
                elif hasattr(x, "__getitem__"):
                    return x[name]
                else:
                    return getattr(x, name)
            except (KeyError, AttributeError):
                continue
        raise NameError(f"Undefined variable '{name}'")
    return getvar

#---- collection objects ----------------------------------------

class CollectibleNDArray(np.ndarray):
    """Numpy array but it collects as sum(x).
    This allows omitting the sum(...) in sum reports.
    If the user _really_ wants to store a list instead, they can collect list(xs). """

    def __collect__(self) -> float:
        return sum(self)

class LazyListDataFrame:
    """Helper class to turn a list[T] info a dataframe-like object where columns are T's fields."""

    def __init__(self, xs: list):
        self._xs = xs

    def __getattr__(self, attr: str) -> np.ndarray:
        arr = np.array([getattr(x, attr) for x in self._xs]).view(CollectibleNDArray)
        setattr(self, attr, arr)
        return arr

    def __getitem__(self, idx: Any) -> Any:
        return self._xs[idx]

    def __iter__(self) -> Iterator[Any]:
        return self._xs.__iter__()

def autocollective(x: Any) -> Any:
    """Automagically turn `x` into a LazyListDataFrame if it's a list."""
    if isinstance(x, list):
        return LazyListDataFrame(x)
    return x
