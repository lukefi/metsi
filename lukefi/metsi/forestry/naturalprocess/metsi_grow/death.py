import math
from .coding import Species
from .kanto import dk
from .math import tolmax, tolmin

#---- jsdeath ----------------------------------------

def _jsdeath(expn: float, step: float) -> float:
    return (1 + math.exp(-min(max(expn, -5.0), 40.0))) ** (-step)

def jsdeath_manty(d: float, rdfl: float, step: float = 5) -> float:
    return _jsdeath(
        8.8165
        - 4.4671 * rdfl
        - 55.5793 * rdfl/dk(d)
    , step)

def jsdeath_kuusi(d: float, rdfl: float, step: float = 5) -> float:
    return _jsdeath(
        8.3970
        - 4.9195 * rdfl
        - 35.6928 * rdfl/dk(d)
    , step)

def jsdeath_raudus(d: float, rdfl: float, step: float = 5) -> float:
    return _jsdeath(
        8.5158
        - 4.8386 * rdfl
        - 34.9224 * rdfl/dk(d)
    , step)

def jsdeath_lehti(spe: Species, d: float, rdfl: float, step: float = 5) -> float:
    return _jsdeath(
        9.0959
        - 1.6857 * int(spe in (Species.ASPEN, Species.BLACK_ALDER))
        - 0.8259 * int(spe == Species.GRAY_ALDER)
        - 2.5000 * int(spe == Species.DECIDUOUS)
        - 5.7434 * rdfl
        - 21.3825 * rdfl/dk(d)
    , step)

def jsdeath(spe: Species, d: float, rdfl: float, step: float = 5) -> float:
    if spe in (Species.PINE, Species.CONIFEROUS):
        return jsdeath_manty(d, rdfl, step)
    elif spe == Species.SPRUCE:
        return jsdeath_kuusi(d, rdfl, step)
    elif spe == Species.SILVER_BIRCH:
        return jsdeath_raudus(d, rdfl, step)
    else:
        return jsdeath_lehti(spe, d, rdfl, step)

def jsdeath_interp(spe: Species, d: float, id: float, rdfl: float, step: float = 5) -> float:
    return jsdeath(
        spe = spe,
        d = d + id*(5-step)/step,
        rdfl = rdfl,
        step = step
    )

#---- pmodel3 ----------------------------------------

def pmodel3a_suo_manty(
    d: float,
    baL: float,
    G: float,
    Grel_lehti: float,
    dg: float,
    step: float = 5
) -> float:
    d = max(d, 1.0)
    expn = (
        5.855+0.04
        - 37.639 * 1/(d*10)
        - 2.02   * baL/G
        - 0.107  * G
        - 2.007  * Grel_lehti
        + 0.11   * dg
    )
    expn = max(tolmin(expn, 85, 40), -5.0)
    return (1.0 + math.exp(-expn))**(-step/5.0)

#---- bmodel3 ----------------------------------------

def bmodel3_suo_koivu(
    d: float,
    baL: float,
    G: float,
    Grel_manty: float,
    dd: float,
    step: float = 5
) -> float:
    d = max(d, 1.0)
    Grel_manty = tolmax(Grel_manty, 0.01, 0.1)
    expn = (
        12.34+0.08
        - 93.18 * 1/(10*d)
        - 1.847 * baL/G
        - 0.083 * G
        + 1.414 * Grel_manty
        - 0.0048 * dd
    )
    expn = max(tolmin(expn, 85, 40), -5.0)
    return (1 + math.exp(-expn))**(-step/5.0)

#---- famort ----------------------------------------

RIAKT = [
    (-0.545454545, 1186.363636),
    (-0.181818182, 595.4545455),
    (-0.181818182, 445.4545455),
    (-0.136363636, 334.0909091),
    (-0.163636364, 400.9090909),
    (-0.090909091, 222.7272727),
    (-0.136363636, 334.0909091),
    (-0.090909091, 472.7272727),
    (-0.090909091, 222.7272727)
]

def famort(
    spe: Species,
    age13: float,
    dd: float,
) -> float:
    a, b = RIAKT[spe-1]
    agemax = b + a*dd
    r0 = math.exp(-10 + 10 * age13 / (0.82 * agemax))
    r5 = math.exp(-10 + 10 * (age13 + 5) / (0.82 * agemax))
    rfam0 = r0 / (1 + r0)
    rfam5 = r5 / (1 + r5)
    return 1 - (rfam5 - rfam0) / (1 - rfam0)
