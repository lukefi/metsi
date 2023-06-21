import builtins
from enum import Enum
from functools import lru_cache, cache
from typing import Any, Optional
from collections.abc import Iterator, Callable
import numpy as np

GetVarFn = Callable[[str], Any]
"""A function that returns the value of a global variable given its name."""

CollectFn = Callable[[GetVarFn], Any]
"""A function that returns the value of a collective expression given the values of global variables."""

#---- collector functions ----------------------------------------

class Globals(dict):
    """Global namespace for collective functions.
    This class is a hack to work around the restriction that `eval` second parameter must be a dict.

    What happens when a global variable is referenced in a collective expression is:
      1. Python looks up the global in the `globals` dict given to `eval`, which in our case
         is a `Globals` instance.
      2. The `Globals` dict is empty, so `__missing__` is called.
      3. `__missing__` calls the proxied `GetVarFn`, returning the actual value of the global
         variable.

    This way we don't need to populate the global variable dict ahead of time, and instead
    we can just dynamically populate the few variables that the expression references."""

    __slots__ = "delegate",

    def __init__(self):
        self.delegate: Optional[GetVarFn] = None

    def __missing__(self, name: str) -> Any:
        return self.delegate(name) # type: ignore -- this shouldn't be called before delegate is set


@lru_cache
def compile(expr: str) -> CollectFn:
    """Compile a Python expression `expr` into a collector function.

    :param expr: A python expression that evaluates to the value of the collected variable.
    :return: A collector function for the expression."""
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
    """Collect variables from a state defined by `getvar`.

    :param collective: Collective expressions keyed by name.
    :param getvar: Values of global variables.
    :return: Values of the collective variables keyed by name."""
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


def autocollective(x: Any, **list_filters) -> Any:
    """
    Automagically turn `x` into a LazyListDataFrame if it's a list.
    :list_filters: define key-value pairs where the key is the filtered attribute,
        and the value is a list of values that correspond the accepted value of that attribute.
    """
    if isinstance(x, list):
        if list_filters:
            for key, values in list_filters.items():
                x = [item for item in x if getattr(item, key) in values]
        return LazyListDataFrame(x)
    return x


def _collector_wrapper(operation_parameters, *aliases, **named_aliases) -> dict[str, Any]:
    getvar = cache(getvarfn(*aliases, **named_aliases))
    return collect_all(operation_parameters, getvar=getvar)


def property_collector(objects: list[object], properties: list[str]) -> list[list]:
    result_rows = []
    for o in objects:
        row = []
        for p in properties:
            if not hasattr(o, p):
                raise Exception(f"Unknown property {p} in {o.__class__}")
            val = o.__getattribute__(p) or 0.0
            if isinstance(val, Enum):
                val = val.value
            row.append(val)
        result_rows.append(row)
    return result_rows
