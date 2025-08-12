from typing import Optional
from .coding import DitchStatus, LandUseCategoryVMI, Origin, SiteTypeVMI, Species, TaxClassReduction, TkgTypeVasanderLaine
import math
from .conv import spe4
from .math import tolmax
from .peat import ojic, peatc
from .regen import agekri_empty, hvalta
from .trans import ba2du, d2bau
from numba import njit
#---- isot puut / suo ----------------------------------------

@njit
def ih5d(h: float, ih5: float, d5: float) -> float:
    h5 = h + ih5
    if h > 2 and h5/d5 > 2:
        ih5 = min(max(2*d5 - h, 0.05), 2.0)
    return ih5

def ih5adj(
    ih5: float,
    G: float,
    dd: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None
) -> float:
    ih5 *= peatc(mal, dd)
    ih5 *= ojic(G, dd, mal, oji, tkg)
    #ih5 = ih5d(h, ih5, d5)
    return tolmax(ih5, 0, 0.05)

def ih5_suo_manty(
    d: float,
    baL: float,
    G: float,
    G_koivu: float,
    hdom100: float,
    dd: float,
    mal: LandUseCategoryVMI,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dnm: float = -1,
    pdr: bool = False,
) -> float:
    if G <= 0.000001 or hdom100 <= 0.000001:
        return 0.05
    if mal > LandUseCategoryVMI.FOREST:
        tkg = TkgTypeVasanderLaine.VATKG1
    dnmts800 = int(0 <= dnm < 20) * int(dd >= 800)
    untr = (
        0.841
        + 0.830 * math.log(d)
        + 0.015 * baL
        - 0.001 * baL**2
        - 0.091 * hdom100
        - 0.760 * d/hdom100
        + 0.196 * G_koivu/G
        - 1.965 * math.expm1(-(dd/1000)**4)
        + 0.257 * dnmts800 * int(tkg == TkgTypeVasanderLaine.MTKG2)
        + 0.257 * dnmts800 * int(tkg in (
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
        + 0.195 * dnmts800 * int(tkg in (
            TkgTypeVasanderLaine.VATKG1,
            TkgTypeVasanderLaine.VATKG2,
            TkgTypeVasanderLaine.JATK
        ))
        - 0.093 * int(pdr)
        - 0.064 * math.log(d) * int(tkg in (
            TkgTypeVasanderLaine.MTKG2,
            TkgTypeVasanderLaine.PTKG1
        ))
        - 0.083 * math.log(d) * int(tkg == TkgTypeVasanderLaine.PTKG2)
        - 0.033 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.VATKG1,
            TkgTypeVasanderLaine.VATKG2,
            TkgTypeVasanderLaine.JATK
        ))
    )
    return math.exp(untr)*1.251/10

def ih5a_suo_manty(
    d: float,
    baL: float,
    snt: Origin,
    G: float,
    G_koivu: float,
    hdom100: float,
    dd: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dnm: float = -1,
    pdr: bool = False,
    jh: float = 0
) -> float:
    ih = ih5_suo_manty(d, baL, G, G_koivu, hdom100, dd, mal, tkg, dnm, pdr)
    ih = ih5adj(ih, G, dd, mal, oji, tkg)
    if snt > Origin.NATURAL:
        ih *= 1 + jh
    return ih

def ih5_suo_kuusi(
    d: float,
    baLku: float,
    hdom100: float,
    dd: float,
    mal: LandUseCategoryVMI,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dr: float = -1,
    dnm: float = -1
) -> float:
    if hdom100 == 0:
        return 0
    if mal > LandUseCategoryVMI.FOREST:
        tkg = TkgTypeVasanderLaine.VATKG1
    untr = (
        1.232
        - 0.0022 * d**1.5
        + 0.936 * math.log(d)
        - 0.034 * baLku
        + 0.118 * math.log(baLku+0.0001)
        - 0.669 * d/hdom100
        + 4.617 * math.log(dd/1000)
        - 0.102 * hdom100 * dd/1000
        - 0.175 * int(dd < 1050) * int(0 <= dr < 5)
        + 0.316 * int(dd < 1050) * int(0 <= dnm < 10)
        + 0.064 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.RHTKG1,
            TkgTypeVasanderLaine.RHTKG2
        ))
        + 0.056 * hdom100 * int(tkg in (
            TkgTypeVasanderLaine.MTKG1,
            TkgTypeVasanderLaine.MTKG2,
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
    )
    c = 1.271 - 0.0055*d
    return c*math.exp(untr)/10

def ih5a_suo_kuusi(
    d: float,
    baLku: float,
    snt: Origin,
    G: float,
    hdom100: float,
    dd: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dr: float = -1,
    dnm: float = -1,
    jh: float = 0
) -> float:
    ih = ih5_suo_kuusi(d, baLku, hdom100, dd, mal, tkg, dr, dnm)
    if ih <= 0:
        return 0.0001
    ih = ih5adj(ih, G, dd, mal, oji, tkg)
    if snt > Origin.NATURAL:
        ih *= 1 + jh
    return ih

def ih5_suo_koivu(
    d: float,
    baLlehti: float,
    dg: float,
    G: float,
    G_manty: float,
    F: float,
    hdom100: float,
    dd: float,
    Z: float,
    mal: LandUseCategoryVMI,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dr: float = -1,
    dnm: float = -1,
    xt_thin: float = -1,
    xt_fert: float = -1
) -> float:
    if mal > LandUseCategoryVMI.FOREST:
        tkg = TkgTypeVasanderLaine.VATKG1
    untr = (
        -14.659
        + 0.679 * math.log(d)
        - 0.006 * baLlehti**1.3
        - 0.079 * hdom100
        - 0.753 * d/hdom100
        - 0.0002 * F/d
        + 0.142 * math.log(F)
        + 2.294 * math.log(dd)
        + 0.002 * Z
        + 0.226 * int(0 <= dr < 5) * int(tkg in (
            TkgTypeVasanderLaine.RHTKG1,
            TkgTypeVasanderLaine.RHTKG2
        ))
        + 0.145 * int(0 <= dnm < 10) * int(tkg in (
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
        + 0.082 * int(5 <= xt_thin < 10)
        - 0.421 * (G_manty/G if G > 0 else 0) * int(tkg in (
            TkgTypeVasanderLaine.RHTKG1,
            TkgTypeVasanderLaine.RHTKG2
        ))
        + 0.009 * dg * int(tkg in (
            TkgTypeVasanderLaine.RHTKG1,
            TkgTypeVasanderLaine.RHTKG2
        ))
        + 0.007 * dg * int(tkg in (
            TkgTypeVasanderLaine.MTKG1,
            TkgTypeVasanderLaine.MTKG2
        ))
        + 0.130 * int(0 <= xt_fert < 15) * int(tkg in (
            TkgTypeVasanderLaine.PTKG1,
            TkgTypeVasanderLaine.PTKG2
        ))
    )
    return (math.exp(untr)*1.187-2)/10

def ih5a_suo_koivu(
    d: float,
    baLlehti: float,
    dg: float,
    G: float,
    G_manty: float,
    F: float,
    hdom100: float,
    dd: float,
    Z: float,
    mal: LandUseCategoryVMI,
    oji: Optional[DitchStatus] = None,
    tkg: Optional[TkgTypeVasanderLaine] = None,
    dr: float = -1,
    dnm: float = -1,
    xt_thin: float = -1,
    xt_fert: float = -1
) -> float:
    ih = ih5_suo_koivu(d, baLlehti, dg, G, G_manty, F, hdom100, dd, Z, mal, tkg, dr, dnm, xt_thin, xt_fert)
    if ih <= 0:
        return 0.0001
    ih = ih5adj(ih, G, dd, mal, oji, tkg)
    return ih

#---- isot puut / kangas ----------------------------------------

PF = [
    (
        6.07, 0.33, 0.33, 4.11,10.16,10.16, 0.00, 0.00, 0.00, 0.00,	
        21.7, 0.00, 0.00,-6.38,-17.2,-19.0, 00.0, 0.00, 0.00, 0.00,			
        -3.08,-0.86, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,	
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.31, .384,
    ),
    (
        3.45, 0.00, 0.00, 8.99, 8.99, 8.99, 0.00, 0.00, 0.00, 0.00,	
        28.1, 6.51, 6.51,-10.5,-16.0,-20.0, 00.0, 0.00, 0.00, 0.00,			
        -3.45,-1.50, 0.70, 0.00, 0.07, 0.00, 0.00, 0.00, 0.00, 0.00,	
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.37, .556,
    ),
    (
        0.0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,	
        32.0, 1.35, 1.35, -8.0,-12.0,-15.0, 0.00, 0.00, 0.00, 0.00,		
        -3.04,-1.48, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,	
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, .662,
    ),
    (
        0.0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        33.9, 3.33, 3.33, -3.0,-8.0,-13.0, 0.00, 0.00, 0.00, 0.00,
        -3.81,-0.86, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, .637
    )
]

PFCR = [
    (
        1.166,1.9,1.9,0.,-1.7,-8.4,-8.4,70.2,-26.5,-17.3,
        2.695,-.238,-.238,0.,.031, .469, .469,-0.071, 0.   ,0.,  
        .521,0.,0.,0.,0.,0.,0.,0., 4.20,0.,
        0.,.00,.326,.082, .025,0.,0.,0.,.223 ,.174 ,
    ),
    (
        1.255, 0., 0.,0.,-6.4,-6.4,-6.4,45.3,-11.6,-8.4,
        -5.922, .313, .313,0.,.551, .551, .551, 5.157,-2.440,0.,
        .966,0.,0.,0.,0.,0.,0.,0., 119,0.,  # XXX: tämän kertoimen varmaan tarkoitus olla 1.19 ?
        0.,.00,.329,.105,-.011,0.,0.,0.,.169 ,.344
    ),
    (
        1.446,0.,0.,0.,  0.,  0.,  0.,21.1,   0.,  0.1,
        -3.109, .024, .136,0.,  0.,   0.,   0.,  .083, 0.   ,0.,  
        .354,0.,0.,0.,0.,0.,0.,0., 2.47,0.,
        0.,.00,  0.,  0.,   0.,0.,0.,0.,.142 ,.410 ,
    ),
    (
        1.675,0.,0.,0.,  0.,  0.,  0.,19.9,   0., -1.5,
        -3.524, .024, .136,0.,  0.,   0.,   0.,  .083, 0.   ,0.,
        .354,0.,0.,0.,0.,0.,0.,0., 2.47,0.,
        0.,.00,  0.,  0.,   0.,0.,0.,0.,.142 ,.410
    )
]

PLKORCR = [1.,1.,1.,1.,.99,.98,.97,.96,.95]

def _ih5_fihucr(
    spe: Species,
    cr: float,
    crkor: float,
    mty: SiteTypeVMI,
    dd: float,
    hdomj: float
) -> float:
    pf = PFCR[spe4(spe)-1]
    A = pf[0] * (
        pf[9]
        + (
            pf[7]
            + pf[1] * int(mty == SiteTypeVMI.OMaT)
            + pf[2] * int(mty == SiteTypeVMI.OMT)
            + pf[3] * int(mty == SiteTypeVMI.MT)
            + pf[4] * int(mty == SiteTypeVMI.VT)
            + pf[5] * int(mty == SiteTypeVMI.CT)
            + pf[6] * int(mty >= SiteTypeVMI.ClT)
        ) * dd/1000
        + pf[8] * (dd/1000)**2
    )
    B = (
        pf[10]
        + pf[11] * int(mty == SiteTypeVMI.OMaT)
        + pf[12] * int(mty == SiteTypeVMI.OMT)
        + pf[13] * int(mty == SiteTypeVMI.MT)
        + pf[14] * int(mty == SiteTypeVMI.VT)
        + pf[15] * int(mty == SiteTypeVMI.CT)
        + pf[16] * int(mty >= SiteTypeVMI.ClT) * dd/1000
        + pf[17] * dd/1000
        + pf[18] * (dd/1000)**2
    )
    dihmax = 5/A
    xm0 = (
        .00889
        + 1.55243  * dihmax
        - 1.02468  * dihmax**2
        + 11.75567 * dihmax**3
    )
    xm = xm0*(1+pf[28]*(1-cr))
    if 0.99 < xm <= 1.0:
        xm = 0.99
    elif 1.0 < xm <= 1.01:
        xm = 1.01
    xk = (2*xm+2)/(1-xm**2)
    xn = A**(1-xm)*xk
    bh = max(xn*hdomj**xm-xk*hdomj, 0.0001)
    loghi1 = B + math.log(bh) + pf[32] + pf[20]*math.log(cr) + (pf[38]+pf[39])/2
    loghi2 = B + math.log(bh) + pf[32] + pf[20]*math.log(cr-crkor) + (pf[38]+pf[39])/2
    kor = PLKORCR[spe4(spe)-1]
    return math.exp(kor*loghi1)/math.exp(kor*loghi2)

@njit
def _ih5_antikali(
    ih: float,
    ig: float,
    d: float,
    h: float
) -> float:
    d2 = ba2du(d2bau(d)+ig*100**2)
    dimrel = (h+ih)/d2
    if dimrel > 2:
        ih = max(2*d2 - h, 0.05)
    return ih

def ih5_fihu(
    spe: Species,
    d: float,
    h: float,
    rdfl: float,
    rdflma: float,
    rdflku: float,
    cr: float,
    crkor: float,
    ig5: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    dd: float,
    hdomj: float,
    jd: float = 0
) -> float:
    if mal == LandUseCategoryVMI.SCRUB:
        mty = SiteTypeVMI.ROCKY
    elif mal == LandUseCategoryVMI.WASTE:
        mty = SiteTypeVMI.MOUNTAIN
    pf = PF[spe4(spe)-1]
    A = (
        pf[0]
        + pf[1] * int(mty == SiteTypeVMI.OMaT)
        + pf[2] * int(mty == SiteTypeVMI.OMT)
        + pf[3] * int(mty == SiteTypeVMI.VT)
        + pf[4] * int(mty == SiteTypeVMI.CT)
        + pf[5] * int(mty >= SiteTypeVMI.ClT)
        + (
            pf[10]
            + pf[11] * int(mty == SiteTypeVMI.OMaT)
            + pf[12] * int(mty == SiteTypeVMI.OMT)
            + pf[13] * int(mty == SiteTypeVMI.VT)
            + pf[14] * int(mty == SiteTypeVMI.CT)
            + pf[15] * (
                int(mty >= SiteTypeVMI.ClT)
                + 0.1  * int(mty == SiteTypeVMI.ROCKY)
                + 0.15 * int(mty == SiteTypeVMI.MOUNTAIN)
            )
        ) * dd/1000
    )
    A *= 1 + jd
    dihmax = pf[30]/A
    xm = (
        -.00889
        + 1.55243  * dihmax
        - 1.02468  * dihmax**2
        + 11.75567 * dihmax**3
    )
    if 0.99 < xm <= 1.0:
        xm = 0.99
    elif 1 < xm <= 1.01:
        xm = 1.01
    xk = (2*xm+2)/(1-xm**2)
    xn = A**(1-xm)*xk
    bh = max(xn*h**xm - xk*h, 0.001)
    rdfl = max(rdfl, 0.1)
    BB = (
        pf[20]
        + pf[21] * rdfl
        + pf[22] * rdflma
        + pf[23] * rdflku
        + pf[24] * (rdfl - rdflma - rdflku)
    )
    ih = math.exp(math.log(bh)+BB)
    if abs(crkor) > 0.005:
        ihc = _ih5_fihucr(spe, cr, crkor, mty, dd, hdomj)
        ih = min(ih, ih*ihc)
    if spe < 8:
        if h > 2:
            ih = _ih5_antikali(ih, ig5, d, h)
        if mal == LandUseCategoryVMI.SCRUB:
            ih *= 600/dd
        if mal == LandUseCategoryVMI.WASTE:
            ih *= 0.25
    return ih

#---- pienet puut ----------------------------------------

def hincu(
    spe: Species,
    age: float,
    h: float,
    snt: Origin,
    mty: SiteTypeVMI,
    dd: float,
    G: float,
    verlt: TaxClassReduction = TaxClassReduction.NONE,
    step: float = 5.0
) -> float:
    t = agekri_empty(spe, mty, snt, dd, verlt, hlim=h, a=0)
    hi = hvalta(spe, t+step, mty, snt, dd, verlt) - hvalta(spe, max(t, 1), mty, snt, dd, verlt)
    if hi <= 0:
        hi = h/age*step
    if G > 10:
        hi /= 1 + 0.005*(G-10)**2
    return hi
