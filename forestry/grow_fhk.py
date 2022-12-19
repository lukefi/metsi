import importlib
import json
from dataclasses import dataclass
from functools import cache
from typing import Any, Callable, Generator, Optional
from forestryfunctions.fhk import definevars
from forestdatamodel.model import ForestStand
import fhk
from forestry.utils.file_io import update_stand_growth

StrArg = str|list[str]
StrArgOpt = Optional[StrArg]


def simvars(graph: fhk.Graph, _step: float = 5):

    @graph.given("step")
    def step() -> float:
        return _step

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
    debug: bool        = False,
    step: float        = 5
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
        simvars(g, step)
        q = g.query(Query)
    if debug:
        print(g.dump(color=True))
    return q

@cache
def getmem() -> fhk.Mem:
    return fhk.Mem()

def grow_fhk(input: tuple[ForestStand, Any], **args) -> tuple[ForestStand, None]:
    stand, _ = input
    step = args.get('step', 5)
    query = getquery(
        fname   = args.get("graph"),
        package = args.get("package"),
        lpath   = args.get("luapath"),
        debug   = args.get("debug"),
        step    = step
    )
    mem = getmem()
    mem.reset()
    res = query(stand, mem=mem)
    diameters = res.d
    heights = res.h
    stems = res.f
    update_stand_growth(stand, diameters, heights, stems, step)
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
