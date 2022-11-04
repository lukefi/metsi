import json
from dataclasses import dataclass
from functools import cache
from typing import Any, Callable, Optional
from forestryfunctions.fhk import definevars
from forestdatamodel.model import ForestStand
import fhk

def simvars(graph: fhk.Graph):

    @graph.given("step")
    def step() -> float:
        return 5

@dataclass
class Query:
    d: list[float] = fhk.root("tree#d'")
    h: list[float] = fhk.root("tree#h'")
    f: list[float] = fhk.root("tree#f'")

@cache
def getquery(
    fname: str,
    lpath: Optional[str] = None,
    debug: bool = False
) -> Callable[..., Query]:
    with fhk.Graph() as g:
        if lpath:
            g.ldef(f'package.path=package.path..";"..{json.dumps(lpath)}')
        if debug:
            g.sethook("v")
        g.read(fname)
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
    query = getquery(args["graph"], lpath=args.get("luapath"), debug=args.get("debug"))
    mem = getmem()
    mem.reset()
    res = query(stand, mem=mem)
    for i,t in enumerate(stand.reference_trees):
        t.breast_height_diameter = res.d[i]
        t.height = res.h[i]
        t.stems_per_ha = res.f[i]
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, None
