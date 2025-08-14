from itertools import compress
from typing import Any, Container, Iterable, Iterator, List, Sequence, Tuple, TypeVar
from .coding import Origin, Species, Storie
from .trans import d2ba
from .typing import Reals
from numba import njit
import numpy as np
T = TypeVar("T")

#---- puuvalinta ----------------------------------------

def pick_in(xs: Iterable[T], ctr: Container[T]) -> Iterator[bool]:
    return (x in ctr for x in xs)

def ba_spe(
    ba: Reals,
    f: Reals,
    spe: Sequence[Species],
    choose: Container[Species]
) -> float:
    return sum(g*f for g,f in compress(zip(ba,f), pick_in(spe, choose)))

#---- keskiarvot ----------------------------------------

def _xg_iter(xdf: Iterator[Tuple[float, float, float]]) -> float:
    s, w = 0, 0
    for x,d,f in xdf:
        s += x*f*d**2
        w += f*d**2
    return s/w if w > 0 else 0

def dg(
    d: Iterable[float],
    f: Iterable[float]
) -> float:
    return _xg_iter(zip(d, d, f))

def xg(
    x: Iterable[float],
    d: Iterable[float],
    f: Iterable[float]
) -> float:
    return _xg_iter(zip(x, d, f))

def dg_subseq(
    d: Iterable[float],
    f: Iterable[float],
    subseq: Iterable[bool]
) -> float:
    return _xg_iter(compress(zip(d,d,f), subseq))

def xg_subseq(
    x: Iterable[float],
    d: Iterable[float],
    f: Iterable[float],
    subseq: Iterable[bool]
) -> float:
    return _xg_iter(compress(zip(x,d,f), subseq))

def dgdom(
    d: Iterable[float],
    f: Iterable[float],
    spe: Sequence[Species],
    storie: Sequence[Storie],
    spedom: Species,
    grow: Storie
) -> float:
    if grow == Storie.LOWER:
        dg_lo = dg_subseq(d, f, (sp == spedom and st == Storie.LOWER for sp,st in zip(spe,storie)))
        dg_up = dg_subseq(d, f, (st == Storie.UPPER for st in storie))
        return dg_lo if dg_lo > 0 else dg_up
    else:
        dg_lo = dg_subseq(d, f, (st == Storie.LOWER for st in storie))
        dg_up = dg_subseq(d, f, (sp == spedom and st == Storie.UPPER for sp,st in zip(spe,storie)))
        return dg_up if dg_up > 0 else dg_lo

#---- summat ----------------------------------------

def dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(x*y for x,y in zip(a,b))

#---- prefix-summat ----------------------------------------

def _prefixsum_sorted(px: Iterator[Tuple[float, float]]) -> Iterator[float]:
    pp, xp = next(px)
    s, n, t = 0, 0, 0
    for pn, xn in px:
        s += xp
        n += 1
        if pn < pp:
            yield from (t+0.5*s for _ in range(n))
            t += s
            s, n = 0, 0
        pp, xp = pn, xn
    s += xp
    yield from (t+0.5*s for _ in range(n+1))

def _prefixsum_subseq(
    p: Reals,
    x: Reals,
    subseqs: Iterable[Iterable[bool]]
) -> List[List[float]]:
    ord = sorted(range(len(p)), key=lambda idx: p[idx], reverse=True)
    out = []
    for ss in subseqs:
        ss = list(ss)
        pfx = _prefixsum_sorted((p[idx], x[idx] if ss[idx] else 0) for idx in ord)
        ps = [0.0] * len(ord)
        for idx,b in zip(ord, pfx):
            ps[idx] = b
        out.append(ps)
    return out

def baL_subseq(
    ba: Reals,
    f: Reals,
    subseqs: Iterable[Iterable[bool]]
) -> List[List[float]]:
    return _prefixsum_subseq(ba, [g*f for g,f in zip(ba,f)], subseqs)

def baL_spe(
    ba: Reals,
    f: Reals,
    spe: Sequence[Species],
    choose: Iterable[Container[Species]]
) -> List[List[float]]:
    return baL_subseq(ba, f, ((s in ctr for s in spe) for ctr in choose))

def ccfL_spe(
    prio: Reals,
    ccf: Reals,
    spe: Sequence[Species],
    choose: Iterable[Container[Species]]
) -> List[List[float]]:
    return _prefixsum_subseq(prio, ccf, ((s in ctr for s in spe) for ctr in choose))

def prefixsum_level(xs: Reals, levels: Iterable[Any]) -> List[float]:
    out = []
    for l,x in zip(levels, xs):
        if l >= len(out):
            out.extend(0 for _ in range(l-len(out)+1))
        out[l] += x
    for i in range(1, len(out)):
        out[i] += out[i-1]
    return out


#---- valtapuut ----------------------------------------

def xdom_sorted(xf: Iterator[Tuple[float, float]], lim: float) -> float:
    s, num = 0, 0
    for x,f in xf:
        if num+f >= lim:
            s += (lim-num)*x
            num = lim
            break
        s += f*x
        num += f
    return s/num if num > 0 else 0

def hdom100_spe(
    h: Reals,
    f: Reals,
    d: Reals,
    storie: Sequence[Storie],
    spe: Sequence[Species],
    choose: Iterable[Container[Species]],
    grow: Storie
) -> List[float]:
    dhfsp = sorted(compress(zip(d,h,f,spe), (s <= grow for s in storie)), reverse=True)
    return [
        xdom_sorted(((h,f) for _,h,f,sp in dhfsp if sp in ctr), lim=100)
        for ctr in choose
    ]

def ddom100_spe(
    f: Reals,
    d: Reals,
    storie: Sequence[Storie],
    spe: Sequence[Species],
    choose: Iterable[Container[Species]],
    grow: Storie
) -> List[float]:
    dfsp = sorted(compress(zip(d,f,spe), (s <= grow for s in storie)), reverse=True)
    return [
        xdom_sorted(((d,f) for d,f,sp in dfsp if sp in ctr), lim=100)
        for ctr in choose
    ]

def xdom100_storie(
    xs: Reals,
    d: Reals,
    f: Reals,
    snt: Sequence[Origin],
    flt: Iterable[Any],
    prt: Origin
) -> float:
    sv = sorted(
        compress(zip((s == prt for s in snt), d, f, xs), flt),
        reverse=True
    )
    return xdom_sorted(
        ((x,f) for _,_,f,x in sv),
        lim=100
    )

#---- keskiarvoa suuremmat valtapuut ----------------------------------------

def avg(xf: Iterator[Tuple[float, float]]) -> float:
    s, w = 0, 0
    for x,f in xf:
        s += x*f
        w += f
    return s/w if w > 0 else 0

def xdomj(
    x: Iterable[float],
    f: Iterable[float],
    d: Iterable[float],
    dlim: float
) -> float:
    return avg((x,f) for x,f,d in zip(x,f,d) if d >= dlim)

#---- siementävät puut ----------------------------------------

def ba_seed(
    f: Reals,
    d: Reals,
    storie: Iterable[Storie]
) -> float:
    return sum(f*d2ba(d) for f,d,s in zip(f, d, storie) if s <= Storie.UPPER)

#---- pääpuulaji ----------------------------------------

def argmax(xs: Iterable[float]) -> int:
    ix = enumerate(xs)
    i,m = next(ix)
    for j,x in ix:
        if x > m:
            i,m = j,x
    return i

def _spe_argmax(xs: Iterable[float]) -> Species:
    return Species(argmax(xs)+1)

def spedom_f(sf: Iterator[Tuple[Species, float]]) -> Species:
    fsu = [0.0] * len(Species)
    for s,f in sf:
        fsu[s-1] += f
    return _spe_argmax(fsu)

def spedom_d(sfd: Iterator[Tuple[Species, float, float]]) -> Species:
    fdsu = [0.0] * len(Species)
    for s,f,d in sfd:
        fdsu[s-1] += f*d
    return _spe_argmax(fdsu)

def spedom_g(sfd: Iterator[Tuple[Species, float, float]]) -> Species:
    fsu = [0.0] * len(Species)
    gsu = [0.0] * len(Species)
    for s,f,d in sfd:
        fsu[s-1] += f
        gsu[s-1] += f*d**2
    return _spe_argmax(g/f if f>0 else 0 for f,g in zip(fsu,gsu))
