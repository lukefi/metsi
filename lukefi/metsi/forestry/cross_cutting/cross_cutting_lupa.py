from functools import cache
from collections.abc import Callable, Sequence

import lupa
from lukefi.metsi.data.enums.internal import TreeSpecies

from pathlib import Path

CrossCutFn = Callable[..., tuple[Sequence[int], Sequence[float], Sequence[float]]]


@cache
def cross_cut_lupa(_pcls, _ptop, _plen, _pval, m, div, nas):
    """Produce a cross-cut wrapper function intialized with the crosscut.lua script using the Lupa bindings."""
    path = Path(__file__).parent.parent.resolve() / "lua" / "crosscut.lua"

    with open(path, "r", encoding="utf-8") as file:
        script = file.read()

    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    fn = lua.execute(script)['aptfunc_lupa']
    _pcls = lua.table_from(_pcls)
    _ptop = lua.table_from(_ptop)
    _plen = lua.table_from(_plen)
    _pval = lua.table_from(_pval)
    aptfunc = fn(_pcls, _ptop, _plen, _pval, m, div, len(nas))

    def cc(
            spe: TreeSpecies,
            d: float,
            h: float
    ):
        vol, val = aptfunc(spe, d, round(h))
        return list(map(int, nas)), list(vol.values()), list(val.values())
    return cc
