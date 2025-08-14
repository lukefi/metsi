import math
from typing import Optional
from .coding import DitchStatus, LandUseCategoryVMI, TkgTypeVasanderLaine

def ojittamattomuus(
    G: float,
    dd: float,
    tkg: Optional[TkgTypeVasanderLaine],
) -> float:
    c = 0.77
    if tkg:
        if tkg <= TkgTypeVasanderLaine.RHTKG2:
            c += 0.15
        elif tkg <= TkgTypeVasanderLaine.MTKG2:
            c += 0.1
    if dd > 400:
        Glim = 2*math.log(min(dd, 1000))
    else:
        Glim = 15
    if G >= Glim:
        c *= 1.02
    return c

def ojic(
    G: float,
    dd: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus],
    tkg: Optional[TkgTypeVasanderLaine]
) -> float:
    if oji == DitchStatus.PEAT_UNDITCHED:
        if mal == LandUseCategoryVMI.FOREST:
            return ojittamattomuus(G, dd, tkg)
        else:
            return 0.77
    else:
        return 1

def peatc(mal: LandUseCategoryVMI, dd: float) -> float:
    c = 1
    if mal >= LandUseCategoryVMI.SCRUB:
        c *= 400/dd
    if mal == LandUseCategoryVMI.WASTE:
        c *= 100/dd
    return c
