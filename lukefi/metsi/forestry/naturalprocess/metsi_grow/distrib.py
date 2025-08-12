import dataclasses
import numpy as np
import math
from typing import Callable, Iterator, List, Tuple
from .aggr import dot
from .coding import Origin, SaplingType, Species, Storie
from .pt import g_nissinen_ko, g_nissinen_ku, g_nissinen_ma
from .trans import d2ba
from .typing import Reals
from scipy.optimize import root

#---- alkulpm ----------------------------------------

def d0_foreco(
    h: float,
    ha: float,
    hdom: float,
    da: float
) -> float:
    logd0 = (
        0.3904
        + 0.9119  * math.log(h-1)
        + 0.05318 * h
        - 1.0845  * math.log(ha)
        + 0.9468  * math.log(da+1)
        - 0.0311  * hdom
    )
    return math.exp(logd0+(0.000478+0.000305+0.03199)/2)

def d0_valkonen(h: float) -> float:
    logd0 = (
        1.5663
        + 0.4559 * math.log(h)
        + 0.0324 * h
    )
    return math.exp(logd0+0.004713/2)-5

#---- näslund pituuskäyrä ----------------------------------------

def naslund_ma_nuori(
    f: float,
    h: float,
    d: float,
    age: float,
    dd: float
) -> Tuple[float, float]:
    b0 = (
        0.708
        - 0.184 * math.log(dd)
        + 0.131 * math.log(age)
        - 0.129 * math.log(f)
        + 2.229 * math.log(d)
        - 2.248 * math.log(h-1)
        + 1.727 * h/d
    )
    b1 = (
        0.339
        - 0.018 * math.log(age)
        + 0.011 * math.log(f)
        + 0.045 * math.log(d)
        - 0.096 * math.log(h-1)
    )
    if b0 < 0.15 or b1 < 0.15:
        b0 = math.exp(
            0.419
            + 1.034 * math.log(d)
            - 1.265 * math.log(h)
            + (0.0486+0.0232)/2
        )
        b1 = math.exp(
            -0.746
            + 0.042 * math.log(d)
            - 0.347 * math.log(h)
            + (0.01078+0.00378)/2
        )
    return b0, b1

def naslund_ma_vanha(
    h: float,
    d: float,
    g: float,
    frel: float,
    dd: float
) -> Tuple[float, float]:
    b0 = (
        3.394
        - 0.296 * math.log(dd)
        - 0.253 * math.log(g/math.sqrt(frel)+1)
        + 0.769 * math.log(d)
        - 0.838 * math.log(h-1)
        + 0.029 * h
    )
    b1 = (
        0.431
        + 0.017 * math.log(g/math.sqrt(frel)+1)
        + 0.034 * math.log(d)
        - 0.136 * math.log(h-1)
    )
    check_H = 1.3 + (d/(b0+b1*d))**2
    virhe_H = (check_H-h)/h
    if d > 0 and abs(virhe_H) >= 0.04:
        b0 = d/math.sqrt(h-1.3) - b1*d
    return b0, b1

def naslund_ku_nuori(
    h: float,
    d: float,
) -> Tuple[float, float]:
    b0 = (
        0.252
        + 1.701 * math.log(d)
        - 1.485 * math.log(h-1)
        + 0.035 * h
    )
    b1 = 0.523 - 0.08 * math.log(h-1)
    if b0 < 0.15 or b1 < 0.15:
        b0 = math.exp(
            0.145
            + 0.913 * math.log(d)
            - 0.844 * math.log(h)
            + (0.0273+0.0086)/2
        )
        b1 = math.exp(
            -0.650
            - 0.185 * math.log(d)
            +(0.00448+0.00098)/2
        )
    return b0, b1

def naslund_ku_vanha(
    h: float,
    d: float,
    dd: float
) -> Tuple[float, float]:
    b0 = (
        3.320
        - 0.365 * math.log(dd)
        + 0.849 * math.log(d)
        - 0.946 * math.log(h-1)
        + 0.057 * h
    )
    b1 = (
        0.584
        + 0.047 * math.log(d)
        - 0.147 * math.log(h-1)
    )
    return b0, b1

def naslund_ko_nuori(
    h: float,
    d: float
) -> Tuple[float, float]:
    b0 = (
        0.824
        + 0.837 * math.log(d)
        - 1.117 * math.log(h-1)
        + 0.067 * math.log(h)
    )
    b1 = 0.470 - 0.106*math.log(h-1)
    if b0 < 0.15 or b1 < 0.15:
        b0 = math.exp(
            0.092
            + 1.018 * math.log(d)
            - 1.109 * math.log(h)
            + (0.0717+0.030)/2
        )
        b1 = math.exp(
            -0.474
            - 0.413 * math.log(h)
            + (0.01156+0.00345)/2
        )
    return b0, b1

def naslund_ko_vanha(
    h: float,
    d: float
) -> Tuple[float, float]:
    b0 = (
        0.853
        + 0.525 * math.log(d)
        - 0.819 * math.log(h-1)
        + 0.058 * h
    )
    b1 = (
        0.504
        + 0.046 * math.log(d)
        - 0.161 * math.log(h-1)
    )
    check_H = 1.3 + (d/(b0+b1*d))**2
    virhe_H = (check_H-h)/h
    if d > 0 and abs(virhe_H) >= 0.04:
        b0 = d/math.sqrt(h-1.3) - b1*d
    return b0, b1

def naslund_b0b1(
    spe: Species,
    use_dg: bool,
    f: float,
    frel: float,
    g: float,
    hx: float,
    dx: float,
    age: float,
    dd: float
) -> Tuple[float, float]:
    if spe == Species.PINE:
        if use_dg:
            return naslund_ma_vanha(hx, dx, g, frel, dd)
        else:
            return naslund_ma_nuori(f, hx, dx, age, dd)
    elif spe == Species.SPRUCE:
        if use_dg:
            return naslund_ku_vanha(hx, dx, dd)
        else:
            return naslund_ku_nuori(hx, dx)
    else:
        if use_dg:
            return naslund_ko_vanha(hx, dx)
        else:
            return naslund_ko_nuori(hx, dx)

#---- weibull ----------------------------------------

def _weib_sample(b: float, c: float, n: int) -> Iterator[float]:
    for i in range(1, n+1):
        ph = (2*i - 1)/(2*n)
        yield b * (-math.log(1-ph))**(1/c)

def weibML_c(
    h: float,
    hdom: float,
    f: float
) -> float:
    return math.exp(
        -2.3529
        + 0.0809 * h
        - 0.0583 * hdom
        + 0.2378 * math.log(f)
        + 1.2920 * 1/math.log(hdom/h+0.4)
    )

@dataclasses.dataclass
class SampleFDH:
    f: List[float]
    d: List[float]
    h: List[float]

def w1_sample(
    h: float,
    d: float,
    f: float,
    hdom: float,
    ddom: float,
    n: int
) -> SampleFDH:
    if hdom <= h:
        hdom = 1.05*h
    if ddom <= d:
        ddom = 1.10*d

    hdom = min(hdom, 5*h)
    ddom = min(ddom, 3*(d+1))

    c = min(max(weibML_c(h, hdom, f), 1.0), 13.0)
    b = h/math.gamma(1 + 1/c)
    hs = list(_weib_sample(b, c, n))
    hsuhde = h / (sum(hs)/n)
    hs = [hi*hsuhde for hi in hs]

    fs = [f/n for _ in range(n)]
    ds = []
    for hx in hs:
        if hx < 1.3:
            ds.append(0)
        elif h > 1.3 and d > 0:
            ds.append(d0_foreco(hx, h, hdom, d))
        else:
            ds.append(d0_valkonen(hx))

    if d > 0:
        dhsuhde = d/(sum(ds)/n)
        if h/d < 2 or dhsuhde > 1:
            ds = [d*dhsuhde for d in ds]

    return SampleFDH(f=fs, d=ds, h=hs)

#---- recovery ----------------------------------------

def w2eq_d(d: float) -> Callable[[Reals], float]:
    # d = bGamma(1 + c^{-1})
    return lambda x: d - x[0]*math.gamma(1+1/x[1])

def w2eq_dgm(dgm: float) -> Callable[[Reals], float]:
    # dgm = cGamma^{-1}(1/2, 1 + 2c^{-1})^{1/c}
    # YAGNI: requires Gamma^{-1}
    raise NotImplementedError("w2 DgM")

def w2eq_dm(dm: float) -> Callable[[Reals], float]:
    # dm = blog(2)^{1/c}
    return lambda x: dm - x[0]*math.log(2)**(1/x[1])

def w2eq_dg(dg: float) -> Callable[[Reals], float]:
    # dg = b(3/2)Gamma(1+3c^{-1})/Gamma(1+2c^{-1})
    # XXX: motissa ei ole 3/2 kerrointa. onko tarkoituksellista?
    return lambda x: dg - x[0]*math.gamma(1+3/x[1])/math.gamma(1+2/x[1])

def w2eq_dq(dq: float) -> Callable[[Reals], float]:
    # dq^2 = b^2*Gamma(1+2c^{-1})
    return lambda x: dq**2 - x[0]**2 * math.gamma(1+2/x[1])

def w2_sample(
    f: float,
    fi: float,
    frel: float,
    g: float,
    gi: float,
    ha: float,
    hgm: float,
    da: float,
    dgm: float,
    dgi: float,
    age: float,
    spe: Species,
    storie: Storie,
    snt: Origin,
    n: int,
    dd: float
) -> SampleFDH:
    use_dg = not (storie <= Storie.UPPER and gi <= 0 and dgi <= 0 and fi > 0)

    n_b0, n_b1 = naslund_b0b1(
        spe = spe,
        use_dg = use_dg,
        f = f,
        frel = frel,
        g = g,
        hx = hgm if use_dg else ha,
        dx = dgm if use_dg else da,
        age = age,
        dd = dd
    )

    if storie == Storie.OVER and (f == fi or g == gi):
        if fi > 0 and gi > 0:
            f, g = fi, gi
        elif fi > 0:
            dq = math.exp(
                0.01413
                + 0.64318 * math.log(da)
                + 0.33557 * math.log(dgm)
                + 0.00175 * dgm
                + 0.0062  * int(snt == Origin.PLANTED)
            )
            dq = max(dq, 0.9*dgm)
            g = fi*d2ba(dq)
        elif gi > 0:
            dq = math.exp(
                0.02957
                + 0.68567 * math.log(da)
                + 0.29178 * math.log(dgm)
                + 0.00156 * dgm
            )
            if dq < 0.9*dgm:
                dq = 0.9*dgm
                use_dg = True
            f = g/d2ba(dq)

    dq = math.sqrt(g/(f*d2ba(1)))

    if use_dg:
        shape = dq/dgm
        if shape > 0.99:
            dq = 0.99*dgm
            if dgm >= 10:
                f = g/d2ba(dq)
            else:
                g = f*d2ba(dq)
        elif shape < 0.4:
            dq = 0.4*dgm
            f, g = (f+g/d2ba(dq))/2, (g+d2ba(dq))/2
        b0 = dq
        c0 = max(1/math.log(dgm**2/dq**2+0.05), 1.0)
        eq1 = w2eq_dg(dgm)
    else:
        if da > dq:
            if spe == Species.PINE:
                g = g_nissinen_ma(da, f, age)
            elif spe == Species.SPRUCE:
                g = g_nissinen_ku(da, f, age)
            else:
                g = g_nissinen_ko(da, f)
            dq = math.sqrt(g/(f*d2ba(1)))
        b0 = max(dq - dq/da, 1.0)
        c0 = 1 / math.log(dq**4/da**4 + 0.1)
        eq1 = w2eq_d(da)

    eq2 = w2eq_dq(dq)
    r = root(lambda x: [eq1(x), eq2(x)], np.array([b0, c0]))
    if not r.success:
        raise ValueError(f"w2 recovery didn't converge: {r.message}")
    b, c = r.x
    ds = list(_weib_sample(b, c, n))
    fs = [f/n for _ in range(n)]

    gero = g - dot(fs, map(d2ba, ds))
    if gero > 0.02 and dgm > 2:
        gin = d2ba(ds[-1]) * fs[-1] + gero
        ds[-1] = math.sqrt(gin/(fs[-1]*d2ba(1)))
        dgdist = sum(f*d**3 for f,d in zip(fs,ds))/sum(f*d**2 for f,d in zip(fs,ds))
        dgkerroin = dgm/dgdist
        if abs(1-dgkerroin) > 0.03:
            if abs(1-dgkerroin) > 0.1:
                dgkerroin = math.sqrt(dgkerroin)
            for i in range(len(ds)-1):
                ds[i] *= dgkerroin

    p = 3.0 if spe == Species.SPRUCE else 2.0
    hs = [1.3 + d**p/(n_b0+n_b1*d)**p for d in ds]

    sd2 = sum(d**2 for d in ds)
    sd2h = sum(h*d**2 for h,d in zip(hs,ds))
    hgpuut = sd2h/sd2
    hgsuhde = hgm/hgpuut
    if hgm > 0 and abs(1-hgsuhde) > 0.03:
        hs = [h*hgsuhde for h in hs]

    return SampleFDH(f=fs, d=ds, h=hs)

#---- rakenne ----------------------------------------

def rakenne(
    f: float,
    fi: float,
    frel: float,
    g: float,
    gi: float,
    ha: float,
    hgm: float,
    hdom: float,
    da: float,
    dgm: float,
    ddom: float,
    dgi: float,
    age: float,
    spe: Species,
    storie: Storie,
    snt: Origin,
    type: SaplingType,
    n: int,
    dd: float
) -> SampleFDH:

    if type == SaplingType.INFEASIBLE:
        s = math.sqrt(math.log(min(f, 50.0))/math.log(f))
        ha *= s
        da *= s
        g *= s

    if hdom <= 5 or dgm < 2:
        if n == 1:
            return SampleFDH(f=[f], d=[da], h=[ha])
        return w1_sample(
            h = ha,
            d = da,
            f = f,
            hdom = hdom,
            ddom = ddom,
            n = n
        )
    else:
        if n == 1:
            return SampleFDH(f=[g/(math.pi/4*(dgm/100)**2)], d=[dgm], h=[hgm])
        return w2_sample(
            f = f,
            fi = fi,
            frel = frel,
            g = g,
            gi = gi,
            ha = ha,
            hgm = hgm,
            da = da,
            dgm = dgm,
            dgi = dgi,
            age = age,
            spe = spe,
            storie = storie,
            snt = snt,
            n = n,
            dd = dd
        )
