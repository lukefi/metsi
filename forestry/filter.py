from typing import Any, Literal
from forestdatamodel.model import ForestStand
from forestry.utils.collectives import GetVarFn, compile, getvarfn

Verb = Literal["select", "remove"]
Object = Literal["stands", "trees", "strata"]


def parsecommand(command: str) -> tuple[Verb, Object]:
    parts = command.split()
    if len(parts) > 2:
        raise ValueError(f"filter syntax error: {command}")
    if len(parts) == 1:
        v, o = parts[0], "stands"
    else:
        v, o = parts
    if v not in Verb.__args__:
        raise ValueError(f"invalid filter verb: {v} (in filter {command})")
    if o not in Object.__args__:
        raise ValueError(f"invalid filter object: {o} (in filter {command})")
    return v, o # type: ignore


def makegetvarfn(named: dict[str, str], *args: Any, **kwargs: Any) -> GetVarFn:
    getnamed = lambda name: compile(named[name])(getvar)
    getvar = getvarfn(*args, getnamed, **kwargs)
    return getvar


def applyfilter(
    stands: list[ForestStand],
    command: str,
    expr: str,
    named: dict[str, str] = {}
) -> list[ForestStand]:
    predicate = compile(expr)
    verb, object = parsecommand(command)
    if verb == "remove":
        p = predicate
        predicate = lambda f: not p(f)
    if object == "stands":
        stands = [
            s
            for s in stands
            if predicate(makegetvarfn(named, s))
        ]
    elif object == "trees":
        for s in stands:
            s.reference_trees = [
                t
                for t in s.reference_trees
                if predicate(makegetvarfn(named, t, stand=s))
            ]
    elif object == "strata":
        for s in stands:
            s.tree_strata = [
                t
                for t in s.tree_strata
                if predicate(makegetvarfn(named, t, stand=s))
            ]
    return stands
