import dataclasses
import math
from typing import List, Optional, Sequence, Tuple
import numpy as np
import numpy.typing as npt
from .coding import LandUseCategoryVMI, Origin, SiteTypeVMI, Species, TaxClass, TaxClassReduction
from .conv import spe4
from .kanto import dk
from .typing import Reals

#---- vmi8-korjaus ----------------------------------------------------

def hd50k_ma(
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    verl: TaxClass,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float
) -> float:
    return (
        .149241
        + .680    * dd/1000
        - .562    * (dd/1000)**2
        - .358054 * xj
        + .176556 * xm
        - .000194 * Z
        - .402331 * int(mal == LandUseCategoryVMI.SCRUB)
        - .7      * int(mal == LandUseCategoryVMI.WASTE)
        + .020707 * int(mty == SiteTypeVMI.VT)
        + .068819 * int(mty == SiteTypeVMI.CT)
        + .0      * int(mty == SiteTypeVMI.ClT)
        - .170542 * int(mty == SiteTypeVMI.ROCKY)
        - .402331 * int(mty == SiteTypeVMI.MOUNTAIN and mal == LandUseCategoryVMI.FOREST)
        - .706770 * int(
            verlt == TaxClassReduction.WET
            and verl >= TaxClass.IB
            and mty <= SiteTypeVMI.MT
        )
        - .252109 * int(
            verlt == TaxClassReduction.STONY
            and verl >= TaxClass.IB
            and mty >= SiteTypeVMI.VT
        )
        - .106470 * int(verlt == TaxClassReduction.WET and mty >= SiteTypeVMI.VT)
    )

def hd50k_ku(
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float
) -> float:
    return (
        -2.055512
        + 3.980   * dd/1000
        - 1.839   * (dd/1000)**2
        - .037887 * xj
        + .664343 * xm
        + .000970 * Z
        + .187935 * int(mal == LandUseCategoryVMI.SCRUB)
        + .2      * int(mal == LandUseCategoryVMI.WASTE)
        + .017290 * int(mty == SiteTypeVMI.OMaT)
        - .070675 * int(mty == SiteTypeVMI.OMT)
        + .019196 * int(mty == SiteTypeVMI.VT)
        + .0      * int(mty == SiteTypeVMI.CT)
        - .1      * int(mty == SiteTypeVMI.ClT)
        + .196336 * int(mty == SiteTypeVMI.ROCKY)
        - .187849 * int(mty == SiteTypeVMI.MOUNTAIN)
        - .074049 * int(verlt == TaxClassReduction.STONY)
        - .099341 * int(verlt == TaxClassReduction.WET)
        - .083910 * int(verlt == TaxClassReduction.MOSS)
    )

def hd50k_ra(
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    verl: TaxClass,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float
) -> float:
    return (
        -1.557652
        + 1.986   * dd/1000
        - .513    * (dd/1000)**2
        - .110713 * xj
        - .108478 * xm
        + .001080 * Z
        - .249864 * int(mal == LandUseCategoryVMI.SCRUB)
        - .3      * int(mal == LandUseCategoryVMI.WASTE)
        + .075057 * int(mty == SiteTypeVMI.OMaT)
        + .075057 * int(mty == SiteTypeVMI.OMT)
        + .234759 * int(mty == SiteTypeVMI.VT)
        + .597830 * int(mty == SiteTypeVMI.CT)
        - .1      * int(mty == SiteTypeVMI.ClT)
        + .169286 * int(mty == SiteTypeVMI.ROCKY)
        + .169287 * int(mty == SiteTypeVMI.MOUNTAIN)
        - .067949 * int(verl == TaxClass.IA)
        + .279850 * int(verlt == TaxClassReduction.WET)
        + .246037 * int(verlt == TaxClassReduction.MOSS)
    )

def hd50k_hi(
    hd50k_ra: float,
    verlt: TaxClassReduction
) -> float:
    return (
        hd50k_ra + .063115
        + .012180 * int(verlt == TaxClassReduction.STONY)
        - .433211 * int(verlt == TaxClassReduction.WET)
    )

def hd50ka(
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float
) -> float:
    return (
        -1.426887 + .0582216
        + 1.838             * dd/1000
        - .540              * (dd/1000)**2
        - .082521           * xj
        - .390489           * xm
        + .000860           * Z
        + .316935           * int(mal == LandUseCategoryVMI.SCRUB)
        - .2                * int(mal == LandUseCategoryVMI.WASTE)
        + .012887           * int(mty == SiteTypeVMI.OMaT)
        + .064706           * int(mty == SiteTypeVMI.OMT)
        + .257001           * int(mty == SiteTypeVMI.VT)
        + .599669           * int(mty == SiteTypeVMI.CT)
        - .1                * int(mty == SiteTypeVMI.ClT)
        + .163237           * int(mty == SiteTypeVMI.ROCKY)
        + .163237           * int(mty == SiteTypeVMI.MOUNTAIN)
        - (.038748+.04955)  * int(verlt == TaxClassReduction.STONY)
        + (.129545-.277663) * int(verlt == TaxClassReduction.WET)
    )

def hd50k_ha(hd50ka: float) -> float:
    return hd50ka + .144658

def hd50k_hl(hd50ka: float) -> float:
    return hd50ka - .080327

def hd50k_tl(hd50ka: float) -> float:
    return hd50ka + .091600

def hd50k_mh(hd50ma: float) -> float:
    return hd50ma - .2

def hd50k_ml(hd50ka: float) -> float:
    return hd50ka + (.085178-.5)

def hd50k(
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    verl: TaxClass,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float
) -> List[float]:
    ma = hd50k_ma(mty, mal, verl, verlt, dd, xj, xm, Z)
    ku = hd50k_ku(mty, mal, verlt, dd, xj, xm, Z)
    ra = hd50k_ra(mty, mal, verl, verlt, dd, xj, xm, Z)
    hi = hd50k_hi(ra, verlt)
    a = hd50ka(mty, mal, verlt, dd, xj, xm, Z)
    ha = hd50k_ha(a)
    hl = hd50k_hl(a)
    tl = hd50k_tl(a)
    mh = hd50k_mh(ma)
    ml = hd50k_ml(a)
    return [ma, ku, ra, hi, ha, hl, tl, mh, ml]

#---- hd50 ---------------------------------------------------

PF = [
    (
        3.578,-6.054,9.718,0.,-6.436,
        .1308,.9913,0.,-1.041,
        1.453,.1385,.0782,-.1363,-.1718,-.1013,-.03647, -.4558,.1647,.0008751,0.,0.,0.,0.,.1385,0.,0.,
    ),
    (
        3.418,-6.337,14.68,0.,-10.56,
        0.,.7811,0.,-.6057,
        1.480,.1874,0.,-.5,-.1631,-.04338,-.08923, -.7855,.08331,0.,0.,0.,0.,0.,.2112,-.2005,0.,
    ),
    (
        3.155,-6.569,-3.379,0.,0.,
        0.,.7313,0.,-.6335,
        .6529,.01246,0.,-.5,-.4450,0.,-.1871, 0.,-.05294,0.,0.,0.,0.,0.,.03087,-.25,.15,
    ),
    (
        2.980,-6.569,-3.379,0.,0.,
        0.,.7313,0.,-.6335,
        .6529,.01246,0.,-.5,-.4450,0.,.1871, 0.,-.05294,0.,0.,0.,0.,0.,.03087,-.25,.15
    )
]

POT = [-.20,-.25,-.5,-.5,-.2,-.2,-.2,-.2,-.2,-.2]

AVER = [0.,.38093,0.,0.,0.,0.,0.,0.,0.,0.]

MINH = [10.,10., 5., 5., 5., 5., 5., 5., 5., 5.]

DA = np.array([
    [.03196,-.1885,8.452,0.,0.,0.],
    [.03083,-.1677,6.782,0.,0.,0.],
    [.005555,0.,0.,0.,0.,0.],
    [.005555,0.,0.,0.,0.,0.]
])

CA = np.array([
    [.00883,0.,0.,0.,0.,0.],
    [.005448,0.,0.,0.,0.,0.],
    [.002690,0.,0.,0.,0.,0.],
    [.002690,0.,0.,0.,0.,0.]
])

EA = np.array([
    [.001045,0.,0.,0.,0.,0.],
    [.001013,0.,0.,0.,0.,0.],
    [.001928,0.,0.,0.,0.,0.],
    [.001928,0.,0.,0.,0.,0.]
])

# huom: tässä pyörii vain pieniä matriiseja, joten matriisiyhtälöitä voisi varmaan siistiä...
# tällä hetkellä suora käännös fortran-koodista, `gaussj` korvattu `np.linalg.solve`:lla.
def _hsatva(
    D: npt.NDArray[np.float64],
    Z: npt.NDArray[np.float64],
    X: npt.NDArray[np.float64],
    rt: npt.NDArray[np.float64],
    c11: float,
    e11: float
) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    kd = D.shape[0]
    num, kdd = Z.shape

    Di = np.empty_like(Z)
    Di[:,:] = 1/c11
    Di[0:kd,0:kd] = np.linalg.inv(D)

    Dd = np.empty_like(Z)
    Dd[:,:] = c11
    Dd[0:kd,0:kd] = D

    W1 = Z/(c11+e11)
    W2 = Z.T @ W1
    W3 = W2 + Di
    VARB = np.linalg.inv(W3)
    W4 = VARB @ Z.T
    W5 = W4 / (c11+e11)
    bm = W5 @ rt

    WW1 = Z/(c11+e11)
    WW2 = WW1 @ VARB
    WW3 = WW2 @ Z.T
    V1 = (np.identity(num)-WW3)/(c11+e11)

    UU1 = Dd @ Z.T
    UU2 = UU1 @ V1
    UU3 = UU2 @ Z
    UU4 = UU3 @ Dd
    UU5 = X.T @ V1
    UU6 = UU5 @ X
    try:
        UU6i = np.linalg.inv(UU6)
    except np.linalg.LinAlgError:
        raise NotImplementedError("TODO: dimensionality reduction (UU6i is singular)")
    UU7 = UU2 @ X
    UU8 = UU7 @ UU6i
    UU9 = UU8 @ X.T
    UU10 = UU9 @ V1
    UU11 = UU10 @ Z
    UU12 = UU11 @ Dd
    VARU = UU4 - UU12
    VARUU = Dd - VARU

    return bm, VARUU

def _hd1(
    pf: Reals,
    mty: SiteTypeVMI,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float,
    agem1: float,
    pert: bool,
    dsuh: float,
    ccfi: float,
) -> float:
    return (
        pf[0]
        + pf[1]  * agem1

        + pf[5]  * ccfi**0.5
        + pf[6]  * math.log(dsuh)
        + pf[7]  * ccfi**0.5 * dsuh**0.5
        + pf[8]  * ccfi * math.log(dsuh)

        + pf[9]  * dd/1000
        + pf[10] * int(mty == SiteTypeVMI.OMT)
        + pf[11] * int(mty == SiteTypeVMI.MT)
        + pf[12] * int(mty >= SiteTypeVMI.CT)
        + pf[13] * int(verlt == TaxClassReduction.MOSS)
        + pf[14] * int(verlt == TaxClassReduction.STONY)
        + pf[15] * int(verlt == TaxClassReduction.WET)
        + pf[16] * xm
        + pf[17] * xj
        + pf[18] * Z
        + pf[19] * int(mty >= SiteTypeVMI.CT) * dd/1000
        + pf[23] * int(mty == SiteTypeVMI.OMaT)
        + pf[24] * int(mty == SiteTypeVMI.VT)
        + pf[20] * agem1 * dd/1000
        + pf[21] * int(mty <= SiteTypeVMI.MT) * agem1
        + pf[22] * int(mty >= SiteTypeVMI.CT) * agem1
        - .25    * int(mty == SiteTypeVMI.ClT)
        + pf[25] * int(pert)
    )

#                     1 2 4
# [1,2,3,4,5,6] --->  2 3 5
#                     4 5 6
# note: you could compute n as
#    n = (sqrt(8m+1)-1)/2
# where m = len(xs).
# but why bother when it's always known by the caller.
def _sym(xs: npt.NDArray[np.float64], n: int) -> npt.NDArray[np.float64]:
    X = np.empty((n,n))
    j,k = 0, 0
    for x in xs:
        X[j,k] = x
        X[k,j] = x
        j += 1
        if j > k:
            k += 1
            j = 0
    return X

def _unsym(X: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    xs = []
    for j in range(X.shape[0]):
        for k in range(j+1):
            xs.append(X[j,k])
    return np.array(xs)

def _var1(da: Reals, sp4z: int) -> float:
    agem1 = 50**POT[sp4z]
    var1 = (
        da[0]
        + da[5] * (agem1-AVER[sp4z])**2
        + da[3] * 2 * (agem1-AVER[sp4z])
    )
    return min(max(var1, 0.00001), 0.25000)

def _hd1ran(
    mty: SiteTypeVMI,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float,
    spedom4z: int,
    pert: bool,
    dmean: float,
    ccfi: float,
    hd50k: float,
    d: Reals,
    h: Reals,
    age: Reals,
) -> Tuple[float, float]:
    n = len(d)
    rt = np.empty(n)
    for i in range(n):
        hd1 = _hd1(
            pf = PF[spedom4z],
            mty = mty,
            verlt = verlt,
            dd = dd,
            xm = xm,
            xj = xj,
            Z = Z,
            agem1 = age[i] ** POT[spedom4z],
            pert = pert,
            dsuh = dmean/dk(d[i]),
            ccfi = ccfi
        )
        apu2 = math.log(max(h[i] - 1.3 - (dmean/dk(d[i])-1), 1))
        rt[i] = apu2 - (hd1+hd50k)

    XAl = []
    if spedom4z == 1:
        XAl.append([ccfi for _ in range(n)])        # 6
    XAl.extend([
        [dmean/math.log(dk(di)) for di in d],       # 7
        [ccfi*dmean/math.log(dk(di)) for di in d],  # 9
        [0 for _ in range(n)],                      # 3
        [0 for _ in range(n)]                       # 5
    ])

    XA = np.array(XAl).T
    xvar1 = XA.sum(axis=0)
    xvar2 = (XA**2).sum(axis=0)
    vvaarr = xvar2 - xvar1**2/n
    X = XA[:,vvaarr!=0]
    c11 = CA[spedom4z][0]
    e11 = EA[spedom4z][0]

    ZZ = np.zeros((n,n+3))
    ZZ[:,0] = 1
    ZZ[:,3:] = np.identity(n)

    bm, varb = _hsatva(
        D = _sym(DA[spedom4z], n=3),
        Z = ZZ,
        X = X,
        rt = rt,
        c11 = c11,
        e11 = e11
    )

    hra = abs(bm[0])
    if 2 <= hra < 4:
        hra = -2 + 3*hra - 5*hra**2
    elif 4 <= hra < 6:
        hra = 6-hra
    elif hra >= 6:
        hra = 0
    hra *= np.sign(bm[0])

    var1 = _var1(da=_unsym(varb), sp4z=spedom4z)

    return hra, var1

@dataclasses.dataclass
class HD50SampleTrees:
    f: Reals
    d: Reals
    h: Reals
    age: Reals
    spe: Sequence[Species]

#@dataclasses.dataclass
#class HD50Result:
#    hd: List[float]
#    hds: float
#    hdtas: List[float]

def hd50(
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    verl: TaxClass,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float,
    prt: Origin,
    spedom: Species,
    ccfi: float,
    trees: Optional[HD50SampleTrees] = None
) -> List[float]:

    # XXX: dd ja Z on väärin päin, vastaa motin bugia.
    # oikea kutsu:
    #     hdk = hd50k(mty, mal, verl, verlt, dd, xj, xm, Z)
    hdk = hd50k(mty, mal, verl, verlt, Z, xj, xm, dd)

    idxd = None
    sp4z = 0 if spedom == Species.CONIFEROUS else min(spedom-1, 3)
    if trees:
        minh = MINH[spedom-1]
        idx = [i for i in range(len(trees.f))
               if trees.d[i]>1.3 and trees.h[i]>0 and trees.age[i]>=minh]
        idxd = [i for i in idx if trees.spe[i]==spedom]
        if idxd:
            hd1ran, var1 = _hd1ran(
                mty = mty,
                verlt = verlt,
                dd = dd,
                xj = xj,
                xm = xm,
                Z = Z,
                spedom4z = sp4z,
                pert = spedom<4 and prt>1,
                dmean = sum(trees.f[i]*dk(trees.d[i]) for i in idx)/sum(trees.f[i] for i in idx),
                ccfi = ccfi,
                hd50k = hdk[spedom-1],
                d = np.array(trees.d)[idxd],
                h = np.array(trees.h)[idxd],
                age = np.array(trees.age)[idxd]
            )
    if not idxd:
        hd1ran = 0
        var1 = _var1(DA[sp4z], sp4z)

    return [
        1.3 + math.exp(hd1ran+var1/2+hdk[sp-1]+_hd1(       # type: ignore
            pf = PF[min(sp,4)-1],
            mty = mty,
            verlt = verlt,
            dd = dd,
            xj = xj,
            xm = xm,
            Z = Z,
            agem1 = 50**POT[min(sp,4)-1],
            pert = spedom<4 and prt>1 and sp==spedom,
            dsuh = 1,
            ccfi = 0.75
        )) for sp in Species
    ]

#---- si --------------------------------------------------------

PAR = [(-2.16,1.459),(-1.54,1.409),(-2.40,1.028),(-2.04,1.020)]
XINDIK = [100.,100.,50.,50.,50.,50.,50.,50.,50.,50.]

HINDPF = [
    (
        6.07, 0.33, 0.33, 4.11,10.16,10.16,10.16, 0.00, 0.00, 0.00,
        21.7, 0.00, 0.00,-6.38,-17.2,-17.2,-17.2, 0.00, 0.00, 0.00,
        -3.08,-0.86, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.31, .384,
    ),
    (
        3.45, 0.00, 0.00, 8.99, 8.99, 8.99, 8.99, 0.00, 0.00, 0.00,
        28.1, 6.51, 6.51,-10.5,-10.5,-10.5,-10.5, 0.00, 0.00, 0.00,
        -3.45,-1.50, 0.70, 0.00, 0.07, 0.00, 0.00, 0.00, 0.00, 0.00,
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.37, .556,
    ),
    (
        0.0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        32.0, 1.35, 1.35, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        -3.04,-1.48, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, .662,
    ),
    (
        0.0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        33.9, 3.33, 3.33, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        -3.81,-0.86, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
        2.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, .637
    )
]

HINDPFK = [
    (0.00, 0.00,1.686,-.0137,-0.829,0.00, 0.00, 0.00, 0.00, .000),
    (.000, .000,-.039, .0088,-0.300,0.00, 0.00, 0.00, 0.00, .000),
    (0.00, 0.00,0.131, .0000, 0.000,0.00, 0.00, 0.00, 0.00, .000),
    (0.00, 0.00,0.944,-.0268, 0.000,0.00, 0.00, 0.00, 0.00, .000)
]

def _hika13a(spe: Species, snt: Origin, h50: float) -> float:
    a, b = PAR[spe4(spe)-1]
    h100 = max(a + b*h50, 10)
    if spe in (Species.DOWNY_BIRCH, Species.GRAY_ALDER, Species.BLACK_ALDER, Species.DECIDUOUS):
        return (14.5+.010417*h100**2-0.68*h100)/.85
    if spe in (Species.SILVER_BIRCH, Species.ASPEN):
        return 14.5+.010417*h100**2-0.68*h100 - 2*int(snt == Origin.PLANTED)
    if spe == Species.SPRUCE and snt != Origin.PLANTED:
        return 35.6+.025794*h100**2-1.65*h100
    if spe == Species.SPRUCE and snt == Origin.PLANTED:
        h25 = math.exp(-3.80985+1.777919*math.log(h100)+.014**2/2)
        ph1 = 1
        while True:
            hh = ph1*(1-math.exp(-.04478*25))**(1-.6564)**(-1)
            if hh >= h25:
                break
        hika13a = 1
        while True:
            hh = ph1*(1-math.exp(-.04478*hika13a))**(1-.6564)**(-1)
            if hh >= 1.3:
                return hika13a-2.5
    if spe in (Species.PINE, Species.CONIFEROUS):
        return 11.5-0.006753*h100**2 + 2*int(snt != Origin.PLANTED)
    assert False

def hind(
    spe: Species,
    mty: SiteTypeVMI,
    verlt: TaxClassReduction,
    dd: float,
    xj: float,
    xm: float,
    Z: float
) -> float:
    sp4 = spe4(spe)
    pf = HINDPF[sp4-1]
    A = (
        pf[0]
        + pf[1] * int(mty == SiteTypeVMI.OMaT)
        + pf[2] * int(mty == SiteTypeVMI.OMT)
        + pf[3] * int(mty == SiteTypeVMI.VT)
        + pf[4] * int(mty == SiteTypeVMI.CT)
        + pf[5] * int(mty == SiteTypeVMI.ClT)
        + (
            pf[10]
            + pf[11] * int(mty == SiteTypeVMI.OMaT)
            + pf[12] * int(mty == SiteTypeVMI.OMT)
            + pf[13] * int(mty == SiteTypeVMI.VT)
            + pf[14] * int(mty == SiteTypeVMI.CT)
            + pf[15] * int(mty >= SiteTypeVMI.ClT)
        ) * dd/1000
    )
    dihmax = pf[30]/A
    xm = -.00889 + 1.55243*dihmax - 1.02468*dihmax**2 + 11.75567*dihmax**3
    if 0.99 < xm <= 1.0:
        xm = 0.99
    elif 1.00 < xm <= 1.01:
        xm = 1.01
    xk = (2*xm+2)/(1-xm**2)
    pfk = HINDPFK[sp4-1]
    pitika = (
        pfk[2]
        + pfk[3] * A
        + pfk[4] * dd/1000
        + pfk[5] * int(mty <= SiteTypeVMI.OMT)
    )
    xkky = (1-xm) * xk * math.exp(pf[20] + 0.1*pf[21] - pitika + pf[39]/2)
    xika13f = 5 * -math.log((1-(1.3/A)**(1-xm)))/xkky
    hd1 = _hd1(
        pf = PF[sp4-1],
        mty = mty,
        verlt = verlt,
        dd = dd,
        xj = xj,
        xm = xm,
        Z = Z,
        agem1 = 50**POT[sp4-1],
        pert = False,
        dsuh = 1,
        ccfi = 0.75
    )
    hdk = 1.3 + math.exp(hd1+0.1**2/2)
    xika13 = _hika13a(
        spe = spe,
        snt = Origin.NATURAL,
        h50 = hdk
    )
    zindik = XINDIK[spe-1] + xika13f - xika13
    return A * (1 - math.exp(-xkky*zindik/5))**(1/(1-xm))
