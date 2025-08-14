import math
from typing import List
import numpy as np
import numpy.typing as npt
from .coding import Species
from .kanto import dk
from .typing import Reals
from numba import njit
#---- jaksoittainen itseharveneminen --------------------------------------------------------------

PS = [
    (12.39130027,-2.06698742,0.57103099),
    (11.87754717,-1.59282869,0.29186363),
    (14.21642186,-2.21782048,0.0),
    (13.17890853,-1.85449784,0.0)
]

PSUO = [
    (13.94229894,-2.05509574,0.0),
    (12.62145978,-1.55383579,0.0),
    (14.21642186,-2.21782048,0.0),
    (13.17890853,-1.85449784,0.0)
]

def _s4(spe: Species) -> int:
    return 1 if spe == Species.CONIFEROUS else min(spe, 4)

# maksimirunkoluvut
def rlmax_kangas(ps: Reals, dk: float, hd50: float) -> float:
    ps_array = np.asarray(ps, dtype=np.float64)
    return _rlmax_kangas_numba(ps_array, dk, hd50)

@njit
def _rlmax_kangas_numba(ps: np.ndarray, dk: float, hd50: float) -> float:
    return np.exp(ps[0]) + ps[1] * np.log(dk) + ps[2] * np.log(hd50)

@njit
def rlmax_suo(psuo: np.ndarray, dk: float) -> float:
    return np.exp(psuo[0] + psuo[1] * np.log(dk))

# jakson sisäinen tiheys

def jak_ma(rlmax4: Reals, wsize: npt.NDArray[np.float64], rdf: Reals, rdftot: float) -> float:
    return (rlmax4[0]*wsize[0,0])*(rdftot-rdf[1])/rdftot + rlmax4[1]*wsize[1,0]*rdf[1]/rdftot

def jak_ku(rlmax4: Reals, wsize: npt.NDArray[np.float64]) -> float:
    return rlmax4[1]*wsize[1,1]

def jak_muut(
    rlmax4: Reals,
    wsize: npt.NDArray[np.float64],
    rdf: Reals,
    rdftot: float,
    spe: Species
) -> float:
    jak = 0
    for spej in Species:
        jak += rlmax4[_s4(spej)-1]*wsize[spej-1,spe-1]*rdf[spej-1]/rdftot
    return jak

def _self_thin_fratio(
    rlmax4: Reals,
    wsize: npt.NDArray[np.float64],
    rdf: Reals,
    rdftot: float,
    f: float
) -> List[float]:
    jak = [
        jak_ma(rlmax4, wsize, rdf, rdftot),
        jak_ku(rlmax4, wsize),
        *(jak_muut(rlmax4, wsize, rdf, rdftot, Species(sp)) for sp in range(3,len(Species)+1))
    ]
    return [f/j if j > 0 else 0 for j in jak]

def wsize_12(hg: Reals) -> npt.NDArray[np.float64]:
    nsp = len(Species)
    wsize = np.empty((nsp, nsp))
    a, b = 0, -6
    for i in range(nsp):
        for j in range(nsp):
            wsize[i,j] = min(max(1 + a/(b-a) + (hg[i]-hg[j])/(b-a), 0), 1)
    return wsize

def self_thin_mineral_12(
    dg: float,
    f: float,
    hg: Reals,
    rdf: Reals,
    rdftot: float,
    hd50_4: Reals
) -> List[float]:
    return _self_thin_fratio(
        rlmax4 = [rlmax_kangas(PS[i], dk(dg), hd50_4[i]) for i in range(4)],
        wsize = wsize_12(hg),
        rdf = rdf,
        rdftot = rdftot,
        f = f
    )

def self_thin_mineral_34(
    dg: float,
    f: float,
    hd50_4: Reals
) -> List[float]:
    return _self_thin_fratio(
        rlmax4 = [rlmax_kangas(PS[i], dk(dg), hd50_4[i]) for i in range(4)],
        wsize = np.ones((9,9)),
        rdf = np.ones(9),
        rdftot = 1,
        f = f
    )

def self_thin_peat_12(
    dg: float,
    f: float,
    hg: Reals,
    rdf: Reals,
    rdftot: float
) -> List[float]:
    return _self_thin_fratio(
        rlmax4 = [rlmax_suo(PSUO[i], dk(dg)) for i in range(4)],
        wsize = wsize_12(hg),
        rdf = rdf,
        rdftot = rdftot,
        f = f
    )

def self_thin_peat_34(
    dg: float,
    f: float
) -> List[float]:
    return _self_thin_fratio(
        rlmax4 = [rlmax_suo(PSUO[i], dk(dg)) for i in range(4)],
        wsize = np.ones((9,9)),
        rdf = np.ones(9),
        rdftot = 1,
        f = f
    )

#---- puittainen itseharveneminen -----------------------------------------------------------------
@njit
def self_thin_tree(dw: float, d: float) -> float:
    return 1/(1+np.exp(2.-5.*(2*d)/(np.sqrt(dw)*(dw-1.))))
