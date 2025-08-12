import dataclasses
import math
import numpy as np
import numpy.typing as npt
from numba import njit, float64
from numba.experimental import jitclass
from .coding import Species

#---- peruskertoimet ----------------------------------------

CRKPK = [
    [2.1288, -0.63157, -1.6082, 2.4886, -2.4147, 2.3619, -1.7539, 1.0817],
    [2.3366, -3.2684, 3.6513, -2.2608, 0., 2.1501, -2.7412, 1.8876],
    [0.93838, 4.1060, -7.8517, 7.8993, -7.5018, 6.3863, -4.3918, 2.1604],
    [1.0600, 3.7233, -7.4110, 7.3395, -6.7216, 5.9156, -4.3415, 1.9663],
    [1.5327, 0.88649, -2.9491, 3.4996, -3.5565, 3.4596, -2.6612, 1.3458],
    [1.9046, 0.49028, -3.4720, 4.5721, -4.4098, 3.7186, -2.5256, 1.4112]
]

CRKPKSP = (0,1,2,2,4,5,5,0,6)

def crkpk(spe: Species) -> npt.NDArray[np.float64]:
    return np.array(CRKPK[CRKPKSP[spe-1]])

#---- korjauspolynomi ----------------------------------------
   #                  5

spec = [
    ('T1', float64),
    ('T4', float64),
    ('T7', float64),
    ('Y1', float64),
    ('Y4', float64),
    ('Y7', float64),
]

@jitclass(spec)
class CrkTY:
    def __init__(self, T1, T4, T7, Y1, Y4, Y7):
        self.T1 = T1
        self.T4 = T4
        self.T7 = T7
        self.Y1 = Y1
        self.Y4 = Y4
        self.Y7 = Y7

@njit
def crkty_ma(d: float, h: float) -> CrkTY:
    dh = d / (h - 1.3)
    dl = np.log(d)
    hl = np.log(h)
    return CrkTY(
        1.100553,
        0.8585458,
        0.5442665,
        0.26222 - 0.0016245*d + 0.010074*h + 0.06273*dh - 0.011971*dh**2 - 0.15496*hl - 0.45333/h,
        -0.38383 - 0.0055445*h - 0.014121*dl + 0.17496*hl + 0.62221/h,
        -0.179 + 0.037116*dh - 0.12667*dl + 0.18974*hl
    )

@njit
def crkty_ku(d: float, h: float) -> CrkTY:
    dh = d / (h-1.3)
    dh2 = dh**2
    dl = np.log(d)
    hl = np.log(h)
    return CrkTY(
        T1 = 1.0814409,
        T4 = 0.8409653,
        T7 = 0.4999158,
        Y1 = -0.003133*d + 0.01172*h + 0.48952*dh - 0.078688*dh2 - 0.31296*dl + 0.13242*hl - 1.2967/h,
        Y4 = -0.0065534*d + 0.011587*h - 0.054213*dh + 0.011557*dh2 + 0.12598/h,
        Y7 = 0.084893 - 0.0064871*d + 0.012711*h - 0.10287*dh + 0.026841*dh2 - 0.01932*dl
    )
@njit
def crkty_ko(d: float, h: float) -> CrkTY:
    d2 = d**2
    dh = d / (h-1.3)
    dh2 = dh**2
    dl = np.log(d)
    hl = np.log(h)
    return CrkTY(
        T1 = 1.084544,
        T4 = 0.8417135,
        T7 = 0.4577622,
        Y1 = 0.59848 + 0.011356*d - 0.49612*dl + 0.46137*hl - 0.92116/dh + 0.25182/dh2 - 0.00019947*d2,
        Y4 = -0.96443 + 0.011401*d + 0.13870*dl + 1.5003/h + 0.57278/dh - 0.18735/dh2 - 0.00026*d2,
        Y7 = -2.1147 + 0.79368*dl - 0.51810*hl + 2.9061/h + 1.6811/dh - 0.40778/dh2 - 0.00011148*d2
    )
@njit
def crkty_le(d: float, h: float) -> CrkTY:
    d2 = d**2
    dh = d / (h-1.3)
    dh2 = dh**2
    dl = np.log(d)
    hl = np.log(h)
    return CrkTY(
        T1 = 1.108743,
        T4 = 0.8186044,
        T7 = 0.4682397,
        Y1 = -1.46153 + 0.0487415*d + 0.663667*dl - 0.827114*hl - 0.00106612*d2 + 1.87966/h + 1.85706/dh - 0.467842/dh2,
        Y4 = -1.24788 - 0.0218693*dh2 + 0.496483*dl - 0.291413*hl + 1.92579/h + 0.863274/dh - 0.183220/dh2,
        Y7 = -0.478730 - 0.104679*dh + 0.151028*dl + 0.882010/h + 0.178386/dh
    )

def crkty(spe: Species, d: float, h: float) -> CrkTY:
    if spe in (Species.PINE, Species.CONIFEROUS):
        return crkty_ma(d, h)
    elif spe == Species.SPRUCE:
        return crkty_ku(d, h)
    else:
        # motin kutsussa näin, alkuperäisessä crk:ssa myös leppä olisi mukana
        return crkty_ko(d, h)



spec3 = [
    ('x1', float64),
    ('x2', float64),
    ('y2', float64),
    ('x3', float64),
    ('y3', float64),
]

@jitclass(spec3)
class CrkP3:
    def __init__(self, x1, x2, y2, x3, y3):
        self.x1 = x1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

@njit
def crktykd(ty: CrkTY) -> CrkP3:
    t1, t4, t7 = ty.T1, ty.T4, ty.T7
    y1, y4, y7 = ty.Y1, ty.Y4, ty.Y7
    y1 = math.copysign(min(abs(y1), 0.1), y1)
    y4 = math.copysign(min(abs(y4), 0.1), y4)
    y7 = math.copysign(min(abs(y7), 0.1), y7)
    return CrkP3(
        x1 = 0.9,
        x2 = 0.6,
        y2 = t1/(t1+y1) * (t4+y4) - t4,
        x3 = 0.3,
        y3 = t1/(t1+y1) * (t7+y7) - t7
    )

def crkkd(spe: Species, d: float, h: float) -> CrkP3:
    return crktykd(crkty(spe, d, h))

def crkkd6(p: CrkP3) -> CrkP3:
    raise NotImplementedError("TODO")

# [ y(0)  = 0 ]
# y(x1) = 0
# y(x2) = y2
# y(x3) = y3
@njit
def cpoly3(p: CrkP3) -> npt.NDArray[np.float64]:
    con1 = p.y2 / (p.x2 * (p.x2-p.x1))
    con2 = p.y3 / (p.x3 * (p.x3-p.x1))
    b3 = (con1-con2) / (p.x2-p.x3)
    b2 = con1 - b3*(p.x1+p.x2)
    b1 = p.x1 * (p.x2*b3 - con1)
    return np.array([b1, b2, b3])

#---- runkokäyrä ----------------------------------------

@dataclasses.dataclass
class Crk:
    c: npt.NDArray[np.float64]  # 1..8
    d80: float                  # 9
    h: float                    # 10

@njit
def xpoly(x: float) -> np.ndarray:
    x2 = x*x
    x3 = x*x2
    x5 = x2*x3
    x8 = x5*x3
    x13 = x8*x5
    x21 = x13*x8
    x34 = x21*x13
    return np.array([x,x2,x3,x5,x8,x13,x21,x34], dtype=np.float64)

def crkpoly(c: npt.NDArray[np.float64], x: float) -> float:
    return max(np.dot(c, xpoly(x)), 0)

# crkpoly^2 antiderivaatta

@njit
def intcrkpoly2(c: np.ndarray, x: float) -> float:
    _, x2, x3, x5, x8, x13, _, _ = xpoly(x)
    c1, c2, c3, c4, c5, c6, c7, c8 = c
    v = c8*c8/69 * x13
    v = (v + c7*c8/28) * x8
    v = (v + c6*c8/24) * x5
    v = (v + (2*c5*c8+c7*c7)/43) * x3
    v = (v + c4*c8/20) * x2
    v = (v + c3*c8/19) * x
    v = (v + c2*c8/18.5) * x
    v = (v + c1*c8/18) * x
    v = (v + c6*c7/17.5) * x5
    v = (v + c5*c7/15) * x3
    v = (v + (2*c4*c7+c6*c6)/27) * x2
    v = (v + c3*c7*0.08) * x
    v = (v + c2*c7/12) * x
    v = (v + c1*c7/11.5) * x
    v = (v + c5*c6/11) * x3
    v = (v + c4*c6/9.5) * x2
    v = (v + (2*c3*c6+c5*c5)/17) * x
    v = (v + c2*c6*0.125) * x
    v = (v + c1*c6/7.5) * x
    v = (v + c4*c5/7) * x2
    v = (v + c3*c5/6) * x
    v = (v + (2*c2*c5+c4*c4)/11) * x
    v = (v + c1*c5*0.2) * x
    v = (v + c3*c4/4.5) * x
    v = (v + c2*c4*0.25) * x
    v = (v + (2*c1*c4+c3*c3)/7) * x
    v = (v + c2*c3/3) * x
    v = (v + c1*c3*0.4+c2*c2*0.2) * x
    v = (v + c1*c2*0.5) * x
    v = (v + c1*c1/3) * x3
    v *= 0.1
    return v

def _crkt(c: npt.NDArray[np.float64], h: float, hx: float) -> float:
    return crkpoly(c, (h-hx)/h)

# crk ilman d6-korjausta; motissa ei käytössä
def ucrkdbh(spe: Species, h: float, hmit: float, d: float) -> Crk:
    c = crkpk(spe)
    da = d
    hd = 1.3
    h += hmit
    if hmit >= 0.01 and h >= 1.5:
        hd += hmit
        da *= _crkt(c,h,1.3) / _crkt(c,h,hd)
    c[:3] += cpoly3(crkkd(spe,da,h))
    d80 = d/_crkt(c,h,hd)
    return Crk(c,d80,h)

def crkv(crk: Crk, h1: float, h2: float) -> float:
    return (
        math.pi/4
        * crk.d80**2
        * crk.h
        * (intcrkpoly2(crk.c, (crk.h-h2)/crk.h) - intcrkpoly2(crk.c, (crk.h-h1)/crk.h))
    )

def crkv0(crk: Crk, h: float) -> float:
    return math.pi/4 * crk.d80**2 * crk.h * intcrkpoly2(crk.c, (crk.h-h)/crk.h)

#---- kannonkorkeus ----------------------------------------

@njit
def hkan_ma(h: float, d: float) -> float:
    return (.09522*h+.4456*d)/100

@njit
def hkan_ku(h: float, d: float) -> float:
    return (.56*h+.5089*d)/100

@njit
def hkan_ko(h: float, d: float) -> float:
    return (.497936*h+.4862*d)/100

@njit
def hkan_ha(d: float) -> float:
    return (math.exp(.509136+.840372*math.log(d))-1)/100

@njit
def hkan_le(h: float, d: float) -> float:
    return max(.785408*d-.156699*h, 0)/100

@njit
def hkan_ml(h: float, d: float) -> float:
    return (0.803156*h+0.101395*d)/100

def hkan(spe: Species, h: float, d: float) -> float:
    if spe in (Species.PINE, Species.CONIFEROUS):
        return hkan_ma(h, d)
    elif spe == Species.SPRUCE:
        return hkan_ku(h, d)
    elif spe in (Species.DOWNY_BIRCH, Species.SILVER_BIRCH):
        return hkan_ko(h, d)
    elif spe == Species.ASPEN:
        return hkan_ha(d)
    elif spe in (Species.GRAY_ALDER, Species.BLACK_ALDER):
        return hkan_le(h, d)
    else:
        return hkan_ml(h, d)
