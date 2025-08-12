import math
from .coding import LandUseCategoryVMI, Origin, SiteTypeVMI, Species
from .conv import spe4
from .kanto import dk as dk13, dkjs_small
from .trans import d2bau
from .typing import Reals

#---- kasvu latvussuhteen kanssa -------------------------------

PFCR = [
    (
        1.500, -0.80,-0.80, 9.20, -1.79,-10.26,-10.26, 26.80,0.,0.,
        -3.715, .013, .013,0., .085,.588,.588,  .432,0.,0.,
        0.445,    0.,    0., 0., 0., 0. ,0., 0., 4.3 ,0.,
        0.,.00,.429,.094,-.030,0.,0.,0.,.133 ,.165 ,
    ),
    (
        1.500,    0.,   0.,26.03, -9.52, -9.52, -9.52, 10.11,0.,0.,
        -4.530, .133, .159,0., .471,.471,.471,  .831,0.,0.,
        1.816,    0.,    0., 0., 0., 0. ,0., 0., 0.0 ,0.,
        0.,.00,.401,.034,-.108,0.,0.,0.,.087 ,.235 ,
    ),
    (
        1.500,    0.,   0.,21.10,    0.,    0.,    0., 12.70,0.,0.,
        -3.086, .044,-.105,0.,   0.,  0.,  0.,-0.317,0.,0.,
        0.528,    0.,    0., 0., 0., 0. ,0., 0., 4.4,0.,
        0.,.00,  0.,  0.,   0.,0.,0.,0.,.150 ,.336 ,
    ),
    (
        1.500,    0.,   0.,20.80,    0.,    0.,    0.,  6.40,0.,0.,
        -1.468, .044,-.105,0.,   0.,  0.,  0.,-1.710,0.,0.,
        0.528,    0.,    0., 0., 0., 0. ,0., 0., 4.4,0.,
        0.,.00,  0.,  0.,   0.,0.,0.,0.,.150 ,.336
    )
]

PLKORCR = [1.,1.,1.,1.,.99,.98,.97,.96,.95]

def _AA_cr(pf: Reals, mty: SiteTypeVMI, dd: float) -> float:
    return (
        pf[7]
        + (
            pf[3]
            + pf[1] * int(mty == SiteTypeVMI.OMaT)
            + pf[2] * int(mty == SiteTypeVMI.OMT)
            + pf[4] * int(mty == SiteTypeVMI.VT)
            + pf[5] * int(mty == SiteTypeVMI.CT)
            + pf[6] * int(mty == SiteTypeVMI.ClT)
        ) * dd/1000
        + pf[8] * (dd/1000)**2
    )

def _A_cr(pf: Reals, mty: SiteTypeVMI, dd: float) -> float:
    return pf[0] * _AA_cr(pf, mty, dd)

def _B_cr(pf: Reals, mty: SiteTypeVMI, dd: float) -> float:
    return (
        pf[10]
        + pf[11] * int(mty == SiteTypeVMI.OMaT)
        + pf[12] * int(mty == SiteTypeVMI.OMT)
        + pf[13] * int(mty == SiteTypeVMI.MT)
        + pf[14] * int(mty == SiteTypeVMI.VT)
        + pf[15] * int(mty == SiteTypeVMI.CT)
        + pf[16] * int(mty == SiteTypeVMI.ClT)
        + pf[17] * dd/1000
        + pf[18] * (dd/1000)**2
    )

def _id_cr(
    pf: Reals,
    kor: float,
    A: float,
    B: float,
    cr: float,
    dk: float,
    snt: Origin
) -> float:
    didmax = (2+1.25*10)/A
    xm0 = (
        -.00889
        + 1.55243  * didmax
        - 1.02468  * didmax**2
        + 11.75567 * didmax**3
    )
    xm = xm0*(1+pf[28])*(1-cr)
    if 0.99 < xm <= 1:
        xm = 0.99
    elif 1 < xm < 1.01:
        xm = 1.01
    xk = (2*xm+2)/(1-xm**2)
    xn = A**(1-xm)*xk
    bd = xn*dk**xm-xk*dk
    bd = max(bd, 0.0001)
    dki = (
        math.log(bd) + B
        + pf[32] * int(snt == Origin.PLANTED)
        + pf[20] * math.log(cr)
        + pf[21] * math.log(cr) * dk
        + pf[22] * math.log(cr)**2
        + (pf[38]+pf[39])/2
    )
    return math.exp(dki*kor)/1.25

def _figu_cr(
    spe: Species,
    d: float,
    dk: float,
    cr: float,
    crkor: float,
    snt: Origin,
    mty: SiteTypeVMI,
    dd: float
) -> float:
    pf = PFCR[spe4(spe)-1]
    kor = PLKORCR[spe-1]
    A = _A_cr(pf, mty, dd)
    B = _B_cr(pf, mty, dd)
    id1 = _id_cr(pf,kor,A,B,cr,dk,snt)
    id2 = _id_cr(pf,kor,A,B,cr+crkor,dk,snt)
    return (d2bau(d+id1)-d2bau(d))/(d2bau(d+id2)-d2bau(d))

#---- yleinen kasvufunktio --------------------------

PFH = [
    (
        6.07, 0.33, 0.33, 4.11,10.16,10.16,   10.16, 0.00, 0.00, 0.00,	
        21.7, 0.00, 0.00,-6.38,-17.2,-17.2,   -17.2, 0.00, 0.00, 0.00,			
    ),
    (
        3.47, 0.00, 0.00, 9.27, 9.27, 9.27,    9.27, 0.00, 0.00, 0.00,	
        27.4, 6.38, 6.38,-9.44,-9.44,-9.44,   -9.44, 0.00, 0.00, 0.00,			
    ),
    (
        -13.9, 0.00, 0.00, 0.00, 0.00, 0.00,    0.00, 0.00, 0.00, 0.00,	
         50.3, 2.49, 2.49,-9.44,-9.44,-9.44,   -9.44, 0.00, 0.00, 0.00,			
    ),
    (
        -11.1, 0.00, 0.00, 0.00, 0.00, 0.00,    0.00, 0.00, 0.00, 0.00,
         40.2, 1.99, 2.49,-9.44,-9.44,-9.44,   -9.44, 0.00, 0.00, 0.00
    )
]

PF = [
    (
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,   0.00, 0.00, 0.00, 0.00,	
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,    0.00, 0.00, 0.00, 0.00,			
        -3.95, 0.02, 0.02,-0.09,-0.34,-0.4,    0.00, 0.00, 0.00,  0.95,	
        -1.83, 0.00, 0.00, 0.00,-0.20, 0.00,  0.00,  0.00,-0.92, 0.00,
         65.2, 0.00,   2.00, 0.00, 16.3, 0.00, 0.00, 0.00, 0.21, .276,
    ),
    (
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,   0.00, 0.00, 0.00, 0.00,	
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,    0.00, 0.00, 0.00, 0.00,	
        -5.47, 0.30, 0.22,-0.12,-0.7,-0.8,    0.00, 0.00, 0.00,  1.61,	
        -1.51, 0.46, 0.00, 0.60,-1.76, 1.08,  0.00,  1.20,-0.50, 0.00,
         99.2, 0.00,   2.00, 0.00, 8.22, 0.00, 0.00, 0.00, 0.41, .288,
    ),
    (
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,   0.00, 0.00, 0.00, 0.00,	
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,    0.00, 0.00, 0.00, 0.00,	
        -4.64, 0.17, 0.17, -0.2,-0.7,-0.8,    0.00, 0.00, 0.00,  1.30,
        -0.50, 0.00, 0.00, 0.00,-2.25, 0.00,  0.00,  0.00,-1.81, 0.00,
         56.7, 0.00,   1.00, 0.00, 16.2, 0.00, 0.00, 0.00, 0.00, .583,
    ),
    (
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,   0.00, 0.00, 0.00, 0.00,
         0.00, 0.00, 0.00, 0.00, 0.00, 0.00,    0.00, 0.00, 0.00, 0.00,
        -4.63, 0.17, 0.17, -0.15,-0.4,-0.5,    0.00, 0.00, 0.00,  0.61,
        -0.21, 0.00, 0.00, 0.00,-2.25, 0.00,  0.00,  0.00,-1.32, 0.00,
         66.7, 0.00,   1.00, 0.00,  8.7, 0.00, 0.00, 0.00, 0.00, .630
    )
]

def _ah_aper(p: Reals, mty: SiteTypeVMI, dd: float) -> float:
    return (
        p[0]
        + p[1] * int(mty == SiteTypeVMI.OMaT)
        + p[2] * int(mty == SiteTypeVMI.OMT)
        + p[3] * int(mty == SiteTypeVMI.VT)
        + p[4] * int(mty == SiteTypeVMI.CT)
        + p[5] * int(mty >= SiteTypeVMI.ClT)
        + (
            p[10]
            + p[11] * int(mty == SiteTypeVMI.OMaT)
            + p[12] * int(mty == SiteTypeVMI.OMT)
            + p[13] * int(mty == SiteTypeVMI.VT)
            + p[14] * int(mty == SiteTypeVMI.CT)
            + p[15] * (
                int(mty >= SiteTypeVMI.ClT)
                + 0.1  * int(mty == SiteTypeVMI.ROCKY)
                + 0.15 * int(mty == SiteTypeVMI.MOUNTAIN)
            )
        ) * (dd/1000)
    )

def _A(pf: Reals, mty: SiteTypeVMI, dd: float) -> float:
    return (
        pf[40]
        + pf[41] * _ah_aper(pf, mty, dd)
    )

def _B(pf: Reals, mty: SiteTypeVMI, dd: float) -> float:
    return (
        pf[20]
        + pf[21] * int(mty == SiteTypeVMI.OMaT)
        + pf[22] * int(mty == SiteTypeVMI.OMT)
        + pf[23] * int(mty == SiteTypeVMI.VT)
        + pf[24] * int(mty == SiteTypeVMI.CT)
        + pf[25] * (
            int(mty >= SiteTypeVMI.ClT)
            + 0.1  * int(mty == SiteTypeVMI.ROCKY)
            + 0.15 * int(mty == SiteTypeVMI.MOUNTAIN)
        )
        + pf[29] * (dd/1000)
    )

def idk(
    spe: Species,
    dk: float,
    rdfl: float,
    rdflma: float,
    rdflku: float,
    rdfl_lehti: float,
    mty: SiteTypeVMI,
    dd: float,
    rdf: float,
    rdfma: float,
    rdfku: float,
    rdf_lehti: float,
    rdfmet: float,
    jd: float = 0
) -> float:
    pf = PF[spe4(spe)-1]
    A = _A(pf, mty, dd) * (1+jd)
    didmax = dk13(pf[42])/A
    xm0 = (
        -.00889
        + 1.55243  * didmax
        - 1.02468  * didmax**2
        + 11.75567 * didmax**3
    )
    xm = xm0 * (1 + pf[43]*rdf + pf[44]*rdfl)
    if 0.99 < xm <= 1.0:
        xm = 0.99
    elif 1.0 < xm <= 1.01:
        xm = 1.01
    xk = (2*xm+2)/(1-xm**2)
    xn = A**(1-xm)*xk
    bd = xn*dk**xm - xk*dk
    bd = max(bd, 0.001)
    dki = (
        math.log(bd) + _B(pf, mty, dd)
        + pf[30] * math.log(1 + rdf)
        + pf[38] * math.log(1 + (rdf-rdfmet))
        + pf[31] * math.log(1 + rdfma)
        + pf[32] * math.log(1 + rdfku)
        + pf[33] * math.log(1 + rdf_lehti)
        + pf[34] * math.log(1 + rdfl)
        + pf[35] * math.log(1 + rdflma)
        + pf[36] * math.log(1 + rdflku)
        + pf[37] * math.log(1 + rdfl_lehti)
    )
    return max(math.exp(dki)/1.25, 0.001)

def ig5_figu(
    spe: Species,
    d: float,
    h: float,
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
    jd: float = 0
) -> float:
    if h <= 3:
        dk = dkjs_small(h)
    else:
        dk = dk13(d)
    if mal == LandUseCategoryVMI.SCRUB:
        mty = SiteTypeVMI.ROCKY
    elif mal == LandUseCategoryVMI.WASTE:
        mty = SiteTypeVMI.MOUNTAIN
    rdfmet = rdf
    id = idk(spe,dk,rdfl,rdflma,rdflku,rdfl_lehti,mty,dd,rdf,rdfma,rdfku,rdf_lehti,rdfmet,jd)
    ig = d2bau(d+id) - d2bau(d)
    if abs(crkor) > 0.005:
        ig = min(ig, ig*_figu_cr(spe,d,dk,cr,crkor,snt,mty,dd))
    ig = max(ig, 0.0001)
    if spe < 8:
        if mal == LandUseCategoryVMI.SCRUB:
            ig *= 600/dd
        elif mal == LandUseCategoryVMI.WASTE:
            ig *= 300/dd
    return ig
