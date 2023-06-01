from collections.abc import Callable


def apply_mappers(target, *mappers: Callable):
    """apply a list of mapper functions to a target object"""
    for mapper in mappers:
        target = mapper(target)
    return target
