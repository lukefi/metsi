import math
from .coding import SiteTypeVMI, Species
from .conv import spe4
from .kanto import dk as dk13

PF = [
    (
        3.861,-.172, -.172, 0.,.066,-.090,-.090,-.462,0.,0.,
        -0.635,-2.079,-0.996,    0.,0.,0.,-.261,-.239,.1632,.1283,
    ),
    (
        5.524, .218, .229,0.,.381,.381,.381,-.187,0.,0.,
        -0.884,-1.833,-1.362,    0.,0.,0.,   0.,   0.,.3480,.2336,
    ),
    (
        2.218, .248, .084,0.,  0.,  0.,  0.,-.595,0.,0.,
        -0.198,-0.988,-0.889,    0.,0.,0.,   0.,   0.,.1269,.1798,
    ),
    (
        2.197, .248, .084,0.,  0.,  0.,  0.,-.595,0.,0.,
        -0.198,-0.988,-0.889,    0.,0.,0.,   0.,   0.,.1269,.1798
    )
]

PLKOR = [1.,1.,1.,1.,.99,.98,.97,.96,.95]

def cr(
    spe: Species,
    rdfl: float,
    mty: SiteTypeVMI,
    dd: float,
    dg: float,
    hg: float,
    rdf: float
) -> float:
    if 0 < hg <= 3:
        dkw = math.exp(0.4163+1.0360*math.log(hg))
    else:
        dkw = dk13(dg)
    pf = PF[spe4(spe)-1]
    A = (
        pf[0]
        + pf[1] * int(mty == SiteTypeVMI.OMaT)
        + pf[2] * int(mty == SiteTypeVMI.OMT)
        + pf[3] * int(mty == SiteTypeVMI.MT)
        + pf[4] * int(mty == SiteTypeVMI.VT)
        + pf[5] * int(mty >= SiteTypeVMI.CT)
        + pf[6] * int(mty >= SiteTypeVMI.ClT)
        + pf[7] * dd/1000
    )
    crf = (
        A
        + pf[10] * math.log(dkw)
        + pf[11] * math.log(1+rdf)
        + pf[12] * math.log(1+rdfl)
        + pf[13] * math.log(1+rdf*rdfl)
    )
    kor = PLKOR[spe4(spe)-1]
    crexp = math.exp(crf*kor)
    return min(crexp/(1+crexp), 0.99)
