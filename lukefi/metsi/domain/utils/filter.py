from typing import Any, Literal, Optional
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.domain.utils.collectives import GetVarFn, compile_collector, getvarfn

Verb = Literal["select", "remove"]
VERBS: set[Verb] = {"select", "remove"}
Object = Literal["stands", "trees", "strata"]
OBJECTS: set[Object] = {"stands", "trees", "strata"}


def parsecommand(command: str) -> tuple[Verb, Object]:
    parts = command.split()
    if len(parts) > 2:
        raise ValueError(f"filter syntax error: {command}")
    if len(parts) == 1:
        v, o = parts[0], "stands"
    else:
        v, o = parts
    if v not in VERBS:
        raise ValueError(f"invalid filter verb: {v} (in filter {command})")
    if o not in OBJECTS:
        raise ValueError(f"invalid filter object: {o} (in filter {command})")
    return v, o # type: ignore


def makegetvarfn(named: dict[str, str], *args: Any, **kwargs: Any) -> GetVarFn:
    getvar: GetVarFn
    def getnamed(name):
        return compile_collector(named[name])(getvar)
    getvar = getvarfn(*args, getnamed, **kwargs)
    return getvar


def applyfilter(
    stands: list[ForestStand],
    command: str,
    expr: str,
    named: Optional[dict[str, str]] = None
) -> list[ForestStand]:
    if named is None:
        named = {}

    predicate = compile_collector(expr)
    verb, object_ = parsecommand(command)
    if verb == "remove":
        p = predicate
        predicate = lambda f: not p(f)  # pylint: disable=unnecessary-lambda-assignment
    if object_ == "stands":
        stands = [
            s
            for s in stands
            if predicate(makegetvarfn(named, s))
        ]
    elif object_ == "trees":
        for s in stands:
            s.reference_trees = [
                t
                for t in s.reference_trees
                if predicate(makegetvarfn(named, t, stand=s))
            ]
    elif object_ == "strata":
        for s in stands:
            s.tree_strata = [
                t
                for t in s.tree_strata
                if predicate(makegetvarfn(named, t, stand=s))
            ]
    return stands
