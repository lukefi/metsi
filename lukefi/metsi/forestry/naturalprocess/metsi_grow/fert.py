import math
from typing import Optional, Sequence, Tuple
from .coding import AddedPhosphorus, FertilizerType, SiteTypeVMI, SoilCategoryVMI, Species, TkgTypeVasanderLaine
from .typing import Reals
from .vol import vol

#---- lannoituskertoimet ----------------------------------------

def fert_a(
    spe: Species,
    d: float,
    h: float,
    id5: float,
    ih5: float,
    fh: float,
    fv: float,
    maxiter: int = 1000,
    eps: float = 0.001
) -> Tuple[float, float]:
    if h < 1.3 or (fh == 0 and fv == 0) or d <= 1 or d >= 53:
        return id5, ih5

    v0 = vol(spe, d, h).tot
    v5 = vol(spe, d+id5, h+ih5).tot
    vt = v5 + (v5-v0)*fv

    hi = h + (1+fh)*ih5
    di = d + id5
    for _ in range(maxiter):
        v = vol(spe, di, hi).tot
        if abs((vt-v0)/(v-v0) - 1) <= eps:
            break
        di *= (vt/v)**(1/4)

    return di-d, hi-h

def fert_b(
    spe: Species,
    d: float,
    h: float,
    id5: float,
    ih5: float,
    fh: float,
    fv: float,
    iter = 50,
    eps = 0.01
) -> float:
    alpha = fh
    v0 = vol(spe, d, h).tot
    v5 = vol(spe, d+(1+alpha)*id5, h+(1+alpha)*ih5).tot
    vt = v5 + (v5-v0)*fv

    for cc in range(1, iter+1):
        if v5 == 0:
            break
        delta = eps * (iter+10-cc)/iter
        if vt > v5:
            alpha += delta
        else:
            alpha -= delta
        v5 = vol(spe, d+(1+alpha)*id5, h+(1+fh)*ih5).tot

    return (1+alpha)*id5

#---- tilavuusvaikutus (kangasmaa) ----------------------------------------

def rfpa(spe: Species, fs: FertilizerType, time: float) -> Reals:
    if spe == Species.PINE:
        if fs in (FertilizerType.AMMONIUM_SULFATE, FertilizerType.CALCIUM_NITRATE):
            return (3.375E-6, 1.0, 3.0, -2.38, 0.324, -0.00072, 7.0, 3.0, 0.0)
        else:
            return (1.718E-6, int(time>1), 3.0, -2.61, 0.39, -0.00083, 7.0, 4.0, 0.0)
    elif spe == Species.SPRUCE:
        if fs in (FertilizerType.AMMONIUM_SULFATE, FertilizerType.CALCIUM_NITRATE):
            return (7.699E-9, 1.0 if time>1 else 0.8, 7.0, -2.02, 0.2, -0.00045, 9.0, 3.0, 2.2)
        else:
            return (2.053E-9, int(time>1), 7.0, -2.09, 0.233, -0.000495, 9.0, 3.0, 2.5)
    assert False

def rfa(spe: Species, fs: FertilizerType, fn: float, time: float) -> float:
    a1, a2, a3, a4, a5, a6, a7, a8, a9 = rfpa(spe, fs, time)
    x = time + (time/a7)**a8 + a9
    d = a4 + a5*math.log(fn+1) + a6*fn
    return a1*a2*x**a3 * math.exp(d*x)

def rfpb(spe: Species, p: AddedPhosphorus) -> Reals:
    if spe == Species.PINE:
        return (-0.00005, 1.5, -0.00564, 0.055, 0.0)
    elif spe == Species.SPRUCE:
        return (-0.00004, 3.0, -0.2, 0.0, 0.012*int(p))
    assert False

def rfb(spe: Species, F: float, hdom: float, h100: float, p: AddedPhosphorus) -> float:
    b1, b2, b3, b4, b5 = rfpb(spe, p)
    f1 = F * hdom * math.exp(b1*F*hdom)
    if b4 > 0:
        f2 = h100**b2 * math.exp(b3*h100**(b4*h100))
    else:
        f2 = h100**b2 * math.exp(b3*h100)*(1+b5*h100)
    return f1 * f2

def rfpc(spe: Species) -> float:
    if spe == Species.PINE:
        return 0.20
    elif spe == Species.SPRUCE:
        return 0.07
    assert False

def rfnr(c: float, time: float, fn: float) -> float:
    return fn/time**(c*time)

def rf(
    spe: Species,
    year: float,
    F: float,
    hdom: float,
    h100: float,
    years: Reals,
    amt: Reals,
    type: Sequence[FertilizerType],
    p: Sequence[AddedPhosphorus]
) -> float:
    ls = rfa(spe, type[0], amt[0], year-years[0]+1)
    c = rfpc(spe)
    for i in range(1,len(years)):
        fns = sum(rfnr(c,years[i]-years[j]+1,amt[j]) for j in range(0,i))
        ls += rfa(spe, type[i], fns+amt[i], year-years[i]+1) - rfa(spe, type[i], fns, year-years[i]+1)
    return ls * rfb(spe, F, hdom, h100, AddedPhosphorus(int(any(p))))

def phma(per: float, hdom: float, age: float) -> float:
    hti = hdom**(-0.4) * age**(-1.1)
    return per * (-0.40006+434.52*hti-124.51*per*hti**2) / 100

def phku(per: float, hdom: float, age: float) -> float:
    hti = hdom**(-0.55) * age**(-1.05)
    return per * (-0.41018+616.4*hti-3592.9*hti**2) / 100

def ph(spe: Species, per: float, hdom: float, age: float) -> float:
    if spe == Species.PINE:
        return phma(per, hdom, age)
    elif spe == Species.SPRUCE:
        return phku(per, hdom, age)
    assert False

def vmthd(spe: Species, age: float, hdom: float, t: float) -> float:
    if t > age:
        per = 1
        while t > age:
            if t-age <= 4:
                per = t-age
            elif hdom >= 5:
                per = 5
            hdom += hdom*ph(spe,per,hdom,age)
            age += per
        return hdom
    else:
        h = hdom
        while True:
            if h <= 5:
                per = 1
            elif age-t <= 4:
                per = age-t
            else:
                per = 5
            while True:
                for _ in range(10):
                    hi = hdom*ph(spe,per,hdom,age-per)
                    if hi >= hdom:
                        if per == 1:
                            return 0
                        break
                    else:
                        hdom = h - hi
                else:
                    if per == 1 or hdom > 5:
                        age -= per
                        if age <= t:
                            return hdom
                        h = hdom
                        break
                hdom, per = h, 1

H100VV = [
    (
        (33.0, 27.0),
        (30.0, 24.0),
        (27.0, 21.0),
        (24.0, 18.0),
        (21.0, 15.0),
        (18.0, 12.0),
        (15.0, 9.0)
    ),
    (
        (30.0, 24.0),
        (27.0, 21.0),
        (24.0, 18.0),
        (21.0, 15.0),
        (18.0, 12.0),
        (15.0, 9.0),
        (12.0, 6.0)
    )
]

def h100vv(spe: Species, mty: SiteTypeVMI, dd: float) -> float:
    p1, p2 = H100VV[spe-1][min(mty,7)-1]
    b = (p1-p2)/(1200-800)
    a = p1-b*1200
    return a+b*dd

def iv_rf_mot(
    mty: SiteTypeVMI,
    dd: float,
    year: float,
    age: float,
    F: float,
    frma: float,
    frku: float,
    years: Reals,
    amt: Reals,
    type: Sequence[FertilizerType],
    p: Sequence[AddedPhosphorus],
    step: int
):
    if age < 1:
        return 0

    age = round(age)

    ds = 0

    if frma > 0 or frku < 1:
        dm = 0
        h100 = h100vv(Species.PINE, mty, dd)
        for i in range(step):
            hdomx = vmthd(Species.PINE, 100, h100, age+i)
            dm += rf(Species.PINE, year+i, F, hdomx, h100, years, amt, type, p)
        ds += (frma + (1-(frma+frku))*0.5)*dm

    if frku > 0:
        dk = 0
        h100 = h100vv(Species.SPRUCE, mty, dd)
        for i in range(step):
            hdomx = vmthd(Species.SPRUCE, 100, h100, age+i)
            dk += rf(Species.SPRUCE, year+i, F, hdomx, h100, years, amt, type, p)
        ds += frku*dk

    ds /= 1.+math.exp(2.4396-0.01236*(dd-600.))
    return ds/step

#---- tilavuusvaikutus (turvemaat) ----------------------------------------

def iv_efe(
    mty: SiteTypeVMI,
    dd: float,
    pd: float,
    hdom: float,
    N0: float,
    V0: float,
    xt_fert: float,
    xt_basicfert: float,
    fert: Optional[FertilizerType],
    tkg: Optional[TkgTypeVasanderLaine] = None,
) -> float:
    if N0 == 0:
        return 0
    cs = int(mty <= SiteTypeVMI.MT or tkg in (
        TkgTypeVasanderLaine.MTKG1,
        TkgTypeVasanderLaine.MTKG2,
        TkgTypeVasanderLaine.PTKG2
    ))
    cs2 = int(mty <= SiteTypeVMI.OMT or tkg == TkgTypeVasanderLaine.MTKG2)
    cs3 = int(mty == SiteTypeVMI.MT or tkg == TkgTypeVasanderLaine.MTKG1)
    cs4 = int(tkg == TkgTypeVasanderLaine.PTKG2)
    cs5 = int(tkg == TkgTypeVasanderLaine.VATKG2)
    if fert in (FertilizerType.PK, FertilizerType.ASH) and (cs2 or cs3):
        pkcs23 = 1 if xt_fert <= 25 else math.exp(-0.25*xt_fert)
    else:
        pkcs23 = 0
    if fert in (FertilizerType.PK, FertilizerType.ASH) and (cs4 or cs5):
        pkcs45 = 1 if xt_fert <= 25 else math.exp(-0.25*xt_fert)
    else:
        pkcs45 = 0
    npkcs23 = int(fert == FertilizerType.NPK and (cs2 or cs3) and xt_fert < 25)
    npkcs45 = int(fert == FertilizerType.NPK and (cs4 or cs5) and xt_fert < 25)
    gs4 = int(mty == SiteTypeVMI.VT or tkg == TkgTypeVasanderLaine.PTKG1)
    gs5 = int(mty == SiteTypeVMI.CT or tkg == TkgTypeVasanderLaine.VATKG1)
    npkgs = int(type == FertilizerType.NPK and (gs4 or gs5))
    return (math.exp(
        -1.3696
        + 0.07296 * int(pd < 1.0)
        + 0.2772  * int(dd >= 1000) * cs2
        + 0.2096  * cs * int(0 < xt_basicfert < 30) * xt_fert**-0.4
        + 1.2011  * V0/(V0+30)
        + 0.2488  * math.log(N0)
        + 0.0202  * hdom
        + 0.1134  * int(dd >= 1000) * pkcs23 * xt_fert * math.exp(-0.11*xt_fert)
        + 0.02376 * int(dd < 1000) * pkcs23 * xt_fert * math.exp(-0.02*xt_fert)
        + 0.02126 * pkcs45 * xt_fert * math.exp(-0.01*xt_fert)
        + 0.07894 * npkcs23 * xt_fert * math.exp(-0.30*xt_fert)
        + 0.2616  * npkcs45 * xt_fert * math.exp(-0.30*xt_fert)
        + 0.1855  * npkgs * xt_fert * math.exp(-0.30*xt_fert)
        + (0.02319 + 0.007704 + 0.02696)/2
    ) - 1) / 100

def iv_fert(
    mty: SiteTypeVMI,
    dd: float,
    pd: float,
    hdom: float,
    N0: float,
    V0: float,
    xt_fert: float,
    xt_basicfert: float,
    type: FertilizerType,
    tkg: Optional[TkgTypeVasanderLaine] = None
) -> float:
    ivu = iv_efe(mty, dd, pd, hdom, N0, V0, xt_fert, xt_basicfert, None, tkg)
    if ivu > 0:
        ivf = iv_efe(mty, dd, pd, hdom, N0, V0, xt_fert, xt_basicfert, type, tkg)
        return (ivf-ivu)/ivu
    else:
        return 0

def iv_ashfert2_efe(
    dd: float,
    V: float,
    N0: float,
    V0: float,
    Pkg: float,
    xt_fert: float
) -> float:
    return math.exp(
        -1.6216
        - 0.1946   * int(dd > 950)
        + 0.8728   * 0.05 * xt_fert*1.5 * math.exp(-0.05*xt_fert*1.5)
        + 0.1516   * math.log(V)
        + 0.007115 * V0
        + 0.2675   * N0
        + 0.7417   * 0.05*Pkg/10 * math.exp(-0.05*Pkg/10) * int(Pkg > 0)
        + 0.6125   * (1 - math.exp(-(xt_fert/15)**2.1)) * int(Pkg > 0)
        - 0.2133   * math.log(V0) * (1 - math.exp(-(xt_fert/15)**2.1)) * int(Pkg > 0)
        + (
            1.3448
            * 0.05*Pkg/10
            * math.exp(-0.05*Pkg/10)
            * int(Pkg > 0)
            * (1 - math.exp(-(xt_fert/15)**2.1))
        )
        + 0.02175
    ) - 1

def iv_ashfert2(
    dd: float,
    V: float,
    N0: float,
    V0: float,
    Pkg: float,
    xt_fert: float
) -> float:
    ivu = iv_ashfert2_efe(dd, V, N0, V0, 0, xt_fert)
    if ivu > 0:
        ivf = iv_ashfert2_efe(dd, V, N0, V0, Pkg, xt_fert)
        return (ivf-ivu)/ivu
    else:
        return 0

#---- pituusvaikutus ----------------------------------------

def pitefe_kangas_ma(dd: float, ccf: float, ccfL: float) -> float:
    return 0.56899 - 0.00022070*dd + 0.16522*ccf - 0.10140*ccfL

def pitefe_kangas_ku(dd: float, ccf: float, ccfL: float) -> float:
    return 1.28212 - 0.00078894*dd + 0.09238*ccf - 0.04001*ccfL

def pitefe_kangas_muu(dd: float, ccf: float, ccfL: float) -> float:
    return 0.92265 - 0.00028771*dd + 0.06672*ccf - 0.01581*ccfL

def pitefe_suo_ma(dd: float, ccf: float, ccfL: float) -> float:
    return 1.91485 - 0.00081061*dd + 0.00000*ccf - 0.00000*ccfL

def pitefe_suo_ku(dd: float, ccf: float, ccfL: float) -> float:
    return 0.86731 - 0.00005239*dd + 0.27369*ccf - 0.09829*ccfL

def pitefe_suo_muu(dd: float, ccf: float, ccfL: float) -> float:
    return 1.04336 - 0.00014331*dd + 0.29746*ccf - 0.29950*ccfL

def ih_hpros(
    alr: SoilCategoryVMI,
    dd: float,
    spe: Species,
    ccf: float,
    ccfL: float,
    vpros: float,
) -> float:
    if alr == SoilCategoryVMI.MINERAL:
        if spe == Species.PINE:
            efe = pitefe_kangas_ma(dd, ccf, ccfL)
        elif spe == Species.SPRUCE:
            efe = pitefe_kangas_ku(dd, ccf, ccfL)
        else:
            efe = pitefe_kangas_muu(dd, ccf, ccfL)
    else:
        if spe == Species.PINE:
            efe = pitefe_suo_ma(dd, ccf, ccfL)
        elif spe == Species.SPRUCE:
            efe = pitefe_suo_ku(dd, ccf, ccfL)
        else:
            efe = pitefe_suo_muu(dd, ccf, ccfL)
    efe = max(efe, 0.001)
    return efe * vpros
