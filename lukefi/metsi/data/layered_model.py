from typing import Any, TypeVar, Union


class LayeredObject[T]:
    _previous: "PossiblyLayered[T]"

    def __init__(self, base: "PossiblyLayered[T]"):
        self._previous = base

    def __getattribute__(self, key):
        local_keys = object.__getattribute__(self, '__dict__').keys()
        builtins = ('__dict__', '__getattribute__', 'new_layer', 'fixate')
        if key in local_keys or key in builtins:
            return object.__getattribute__(self, key)
        return object.__getattribute__(self, '_previous').__getattribute__(key)

    def __setattr__(self, name: str, value: Any) -> None:
        object.__setattr__(self, name, value)

    def new_layer(self) -> "LayeredObject[T]":
        return LayeredObject(self)

    def fixate(self) -> "PossiblyLayered[T]":
        root: PossiblyLayered[T]
        if isinstance(self._previous, LayeredObject):
            root = self._previous.fixate()
        else:
            root = self._previous
        root.__dict__.update(self.__dict__)
        return root


T = TypeVar("T")
PossiblyLayered = Union[T, LayeredObject[T]]
