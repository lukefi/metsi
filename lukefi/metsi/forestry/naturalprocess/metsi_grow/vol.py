import dataclasses
import math
from typing import List
from .coding import Species
from .vdata import *
from numba import njit
vmin = 0.0004
vmax = 0.00101788
hmin = 0.00001

@njit
def _biint(ya: np.ndarray, d: float, h: float, xd: np.ndarray, xh: np.ndarray) -> float:
    j = int(max(d - 2.0, 0.0))
    k = int(max(h - 2.0, 0.0))

    y1 = ya[38 * j     + k]
    y2 = ya[38 * (j+1) + k]
    y3 = ya[38 * (j+1) + k + 1]
    y4 = ya[38 * j     + k + 1]

    t = (d - xd[j]) / (xd[j+1] - xd[j])
    u = (h - xh[k]) / (xh[k+1] - xh[k])

    return (1 - t)*(1 - u)*y1 + t*(1 - u)*y2 + t*u*y3 + (1 - t)*u*y4


@dataclasses.dataclass
class Volume:
    tot: float
    saw: float
    pulp: float
    waste: float

def vol(
    spe: Species,
    d: float,
    h: float
) -> Volume:
    if spe in (Species.PINE, Species.CONIFEROUS):
        tot, tuk, lat = vtotm, vtukm, vlatm
    elif spe == Species.SPRUCE:
        tot, tuk, lat = vtotk, vtukk, vlatk
    else:
        tot, tuk, lat = vtotko, vtukko, vlatko
    id = min(d, 59)
    ih = min(h, 38)
    ytuk = _biint(tuk, id, ih, xd, xh)
    if h < hmin:
        ytot, ylat = 0, 0
    else:
        ytot = _biint(tot, id, ih, xd, xh)
        if ytot < vmin:
            ytot = max(min(h*math.pi*((1.2*d/200)**2)/3, vmax), vmin)
            ylat = ytot
        else:
            ylat = _biint(lat, id, ih, xd, xh)
    return Volume(
        ytot,
        ytuk,
        ytot - ytuk - ylat,
        ylat
    )
