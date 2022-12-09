import importlib
import json
from dataclasses import dataclass
from functools import cache
from typing import Any, Callable, Generator, Optional
from forestryfunctions.fhk import definevars
from forestdatamodel.model import ForestStand
import fhk

StrArg = str|list[str]
StrArgOpt = Optional[StrArg]

def simvars(graph: fhk.Graph):

    @graph.given("step")
    def step() -> float:
        return 5

@dataclass
class Query:
    d: list[float] = fhk.root("tree#d'")
    h: list[float] = fhk.root("tree#h'")
    f: list[float] = fhk.root("tree#f'")

def iterargs(x: StrArgOpt) -> Generator[str, None, None]:
    if isinstance(x, str):
        yield x
    elif x:
        yield from x

@cache
def getquery(
    fname: StrArgOpt   = None,
    package: StrArgOpt = None,
    lpath: StrArgOpt   = None,
    debug: bool        = False
) -> Callable[..., Query]:
    with fhk.Graph() as g:
        for p in iterargs(lpath):
            g.ldef(f'package.path=package.path..";"..{json.dumps(p)}')
        for p in iterargs(package):
            getattr(importlib.import_module(p), "register_graph")(g)
        if debug:
            g.sethook("v")
        for f in iterargs(fname):
            g.read(f)
        definevars(g)
        simvars(g)
        q = g.query(Query)
    if debug:
        print(g.dump(color=True))
    return q

@cache
def getmem() -> fhk.Mem:
    return fhk.Mem()

def grow_fhk(input: tuple[ForestStand, Any], **args) -> tuple[ForestStand, None]:
    stand, _ = input
    query = getquery(
        fname   = args.get("graph"),
        package = args.get("package"),
        lpath   = args.get("luapath"),
        debug   = args.get("debug")
    )
    mem = getmem()
    mem.reset()
    res = query(stand, mem=mem)
    for i,t in enumerate(stand.reference_trees):
        height_before_growth = t.height
        t.breast_height_diameter = res.d[i]
        t.height = res.h[i]
        t.stems_per_ha = res.f[i]
        t.biological_age += 5
        if height_before_growth < 1.3 <= t.height:
            t.breast_height_age = t.biological_age
        if t.height >= 1.3 and t.sapling:
            t.sapling = False
    # prune dead trees
    stand.year += 5
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
