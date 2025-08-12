import math
from typing import Optional
from .trans import ba2du
from .coding import DitchStatus, LandUseCategoryVMI, Origin, PeatTypeSINKA, SiteTypeVMI, Species, TkgTypeVasanderLaine
from .ig import ig5_figu
from .peat import ojic, peatc

# TODO: jos ojitustila=2 ja mal=1 niin mal←2 kaikissa peat/id5 malleissa

def id5_suo_manty(
    d: float,
    baL: float,
    G: float,
    hdom100: float,
    dd: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    sty: Optional[PeatTypeSINKA] = None,
    rimp: bool = False,
    pdr: bool = False,
    dr: float = -1,
    dnm: float = -1,
    xt_thin: float = -1
) -> float:
    if mal > LandUseCategoryVMI.FOREST:
        tkg = TkgTypeVasanderLaine.VATKG1
    untr = (
        3.035
        + 0.987 * math.log(d)
        - 0.001 * d**1.5
        - 0.271 * math.log(G)
        - 0.011 * baL
        - 0.0003 * baL**2
        - 0.680 * math.log(hdom100)
        - 0.658 * d/hdom100
        - 0.949 * math.expm1(-(dd/1000)**4)
        + 0.271 * int(0 <= dr < 5) * int(dd >= 1000)
        + 0.106 * int(5 <= dr < 15)
        - 0.075 * int(dr > 20)
        + 0.052 * int(0 <= dnm < 5)
        - 0.297 * int(pdr)
        + 0.090 * int(pdr) * math.log(G)
        + 0.044 * int(5 <= xt_thin <= 10)
        - 0.076 * math.log(d) * int(tkg in (
            TkgTypeVasanderLaine.RHTKG1,
            TkgTypeVasanderLaine.RHTKG2,
            TkgTypeVasanderLaine.MTKG1
        ))
        - 0.112 * math.log(d) * int(tkg in (
            TkgTypeVasanderLaine.MTKG2,
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
        - 0.024 * math.log(d) * int(
            tkg == TkgTypeVasanderLaine.PTKG1
            and sty in (
                PeatTypeSINKA.PsK,
                PeatTypeSINKA.PKgK,
                PeatTypeSINKA.PsR,
                PeatTypeSINKA.KgR,
                PeatTypeSINKA.PKR
            )
        )
        - 0.056 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.VATKG1,
            TkgTypeVasanderLaine.VATKG2,
            TkgTypeVasanderLaine.JATK
        ))
        - 0.442 * int(rimp)
    )
    c = peatc(mal, dd) * ojic(G, dd, mal, oji, tkg)
    id = c * (math.exp(untr + (0.055+0.026+0.186)/2) - 2) / 10
    if id <= 0:
        id = 0.0001
    return id

def id5_suo_kuusi(
    d: float,
    baLku: float,
    G: float,
    hdom100: float,
    dd: float,
    Z: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dr: float = -1,
    dnm: float = -1,
    xt_thin: float = -1
) -> float:
    if mal > LandUseCategoryVMI.FOREST:
        tkg = TkgTypeVasanderLaine.VATKG1
    untr = (
        2.250
        + 0.046 * d
        - 0.001 * d**2
        - 0.132 * math.log(G)
        - 0.022 * baLku
        - 0.115 * (d/hdom100)**2
        - 1.228 * math.expm1(-(dd/1000)**4)
        + 0.001 * Z
        - 0.060 * int(dr > 25)
        + 0.092 * int(dd < 1050) * int(0 <= dnm <= 5)
        - 0.085 * int(0 <= xt_thin <= 900)
        - 0.009 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.MTKG1,
            TkgTypeVasanderLaine.MTKG2
        ))
        - 0.011 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
        - 0.049 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.VATKG1,
            TkgTypeVasanderLaine.VATKG2,
            TkgTypeVasanderLaine.JATK
        ))
    )
    c = peatc(mal, dd) * ojic(G, dd, mal, oji, tkg)
    return max(c * (math.exp(untr + (0.054+0.021+0.122)/2) - 4) / 10, 0)

def id5_suo_koivu(
    d: float,
    baLlehti: float,
    G: float,
    hdom100: float,
    dd: float,
    Z: float,
    mal: LandUseCategoryVMI,
    oji:  Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dr: float = -1,
    dnm: float = -1,
    xt_thin: float = -1,
    xt_fert: float = -1
) -> float:
    if mal > LandUseCategoryVMI.FOREST:
        tkg = TkgTypeVasanderLaine.VATKG1
    untr = (
        -7.332
        + 0.666 * math.log(d)
        - 0.172 * math.log(G)
        - 0.022 * baLlehti
        - 0.074 * hdom100
        - 0.564 * d/hdom100
        + 1.471 * math.log(dd)
        + 0.001 * Z
        + 0.148 * int(0 <= dr < 10)
        + 0.081 * int(10 <= dr < 15)
        - 0.037 * int(dr > 20)
        + 0.070 * int(0 <= dnm < 5) * int(dd >= 800) * int(tkg in (
            TkgTypeVasanderLaine.MTKG2,
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
        + 0.033 * int(0 <= xt_thin <= 5)
        + 0.064 * int(tkg in (
            TkgTypeVasanderLaine.RHTKG1,
            TkgTypeVasanderLaine.RHTKG2
        ))
        + 0.239 * int(0 <= xt_fert <= 25) * int(tkg in (
            TkgTypeVasanderLaine.MTKG2,
            TkgTypeVasanderLaine.PTKG2
        ))
    )
    c = peatc(mal, dd) * ojic(G, dd, mal, oji, tkg)
    return max(c * (math.exp(untr + (0.038+0.014+0.139)/2) - 4) / 10, 0)

def id_init(
    spe: Species,
    h: float,
    ih5: float,
    rdfl: float,
    rdflma: float,
    rdflku: float,
    rdfl_lehti: float,
    cr: float,
    crkor: float,
    snt: Origin,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    dd: float,
    rdf: float,
    rdfma: float,
    rdfku: float,
    rdf_lehti: float,
    jd: float = 0,
    step: float = 5
) -> float:
    if h + ih5 < 1.3:
        return 0
    ig = ig5_figu(
        spe = spe,
        h = h,
        d = 0.01,
        rdfl = rdfl,
        rdflma = rdflma,
        rdflku = rdflku,
        rdfl_lehti = rdfl_lehti,
        cr = cr,
        crkor = crkor,
        snt = snt,
        mty = mty,
        mal = mal,
        dd = dd,
        rdf = rdf,
        rdfma = rdfma,
        rdfku = rdfku,
        rdf_lehti = rdf_lehti,
        jd = jd
    )
    ga = 2
    da = ba2du(ga)
    return da + (ba2du(ga+ig)-da)*(step/5.0)*(1-(1.3-h)/ih5)
