from dataclasses import dataclass
import importlib
import json
import fhk
from lukefi.metsi.data.model import ForestStand
from domain.natural_processes.grow_motti import spe2motti
from domain.natural_processes.util import update_stand_growth
from functools import cache
from typing import Any, Callable, Generator, Optional

StrArg = str|list[str]
StrArgOpt = Optional[StrArg]


def definevars(graph: fhk.Graph):

    #---- global variables ----------------------------------------

    @graph.given("year")
    def year(stand: ForestStand) -> float:
        """Calendar year which the stand data represents"""
        return stand.year

    #---- site variables ----------------------------------------

    @graph.given("site")
    def group_site() -> fhk.Subset:
        """Prepare FHK site (stand) group"""
        return fhk.interval1(1)

    @graph.given("site#mty")
    def site_mty(stand: ForestStand) -> int:
        """Stand site type category"""
        return int(stand.site_type_category)

    @graph.given("site#mal")
    def site_mal(stand: ForestStand) -> int:
        """Stand land use category"""
        return int(stand.land_use_category)

    @graph.given("site#alr")
    def site_alr(stand: ForestStand) -> int:
        """Stand soil and peatland category"""
        return int(stand.soil_peatland_category)

    @graph.given("site#verl")
    def site_verl(stand: ForestStand) -> int:
        """Stand taxation class"""
        return int(stand.tax_class)

    @graph.given("site#verlt")
    def site_verlt(stand: ForestStand) -> int:
        """Stand tax class reduction class"""
        return int(stand.tax_class_reduction)

    @graph.given("site#spedom")
    def site_spedom(stand: ForestStand) -> int:
        return 1 # TODO (see grow_motti)

    @graph.given("site#prt")
    def site_prt(stand: ForestStand) -> int:
        return 1 # TODO (see grow_motti)

    @graph.given("site#Y")
    def site_Y(stand: ForestStand) -> float:
        """latitude assumed to be EPSG:2393 CRS value divided by 1000"""
        return stand.geo_location[0]

    @graph.given("site#X")
    def site_X(stand: ForestStand) -> float:
        """longitude assumed to be EPSG:2393 CRS value divided by 1000"""
        return stand.geo_location[1]

    @graph.given("site#Z")
    def site_Z(stand: ForestStand) -> float:
        """Stand altitude above sea level (m)"""
        return stand.geo_location[2]

    @graph.given("site#dd")
    def site_dd(stand: ForestStand) -> float:
        """Temperature (C) sum of the stand """
        return stand.degree_days

    @graph.given("site#sea")
    def site_sea(stand: ForestStand) -> float:
        """Sea effect value of the stand"""
        return stand.sea_effect

    @graph.given("site#lake")
    def site_lake(stand: ForestStand) -> float:
        """Lake effect value of the stand"""
        return stand.lake_effect

    #---- tree variables ----------------------------------------

    @graph.given("tree")
    def group_tree(stand: ForestStand) -> fhk.Subset:
        """Prepare FHK tree group with reference tree list length"""
        return fhk.interval1(len(stand.reference_trees))

    @graph.given("tree#->site", ldef="mode 's'")
    def tree2site() -> fhk.Subset:
        return 0

    @graph.given("tree#f")
    def tree_f(stand: ForestStand, idx: int) -> float:
        """Tree stem count per hectare"""
        return stand.reference_trees[idx].stems_per_ha

    @graph.given("tree#spe")
    def tree_spe(stand: ForestStand, idx: int) -> int:
        return spe2motti(stand.reference_trees[idx].species)

    @graph.given("tree#d")
    def tree_d(stand: ForestStand, idx: int) -> float:
        """Breast height diameter (cm)"""
        return stand.reference_trees[idx].breast_height_diameter

    @graph.given("tree#h")
    def tree_h(stand: ForestStand, idx: int) -> float:
        """Height (m)"""
        return stand.reference_trees[idx].height

    @graph.given("tree#storie")
    def tree_storie(stand: ForestStand, idx: int) -> int:
        return 0 # TODO

    @graph.given("tree#snt")
    def tree_snt(stand: ForestStand, idx: int) -> int:
        """Origin of trees. Our coding (RSD) matches, but is offset by 1."""
        return (stand.reference_trees[idx].origin or 0) + 1

    @graph.given("tree#t0")
    def tree_t0(stand: ForestStand, idx: int) -> float:
        """Year of birth computed from stand year and tree age"""
        return stand.year - stand.reference_trees[idx].biological_age

    @graph.given("tree#t13")
    def tree_t13(stand: ForestStand, idx: int) -> float:
        """Breast height achievement year computed from stand year and breast height age"""
        return stand.year - stand.reference_trees[idx].breast_height_age


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
