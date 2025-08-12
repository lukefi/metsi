import dataclasses
import math
from typing import List, Tuple
import numpy as np
import numpy.typing as npt
from numba import njit
from .ilmdata import asemko8110, ilmon8110, merja

@njit
def flase(xxa: float, xxo: float) -> tuple:
    R1, R2 = 3.0, 4.0
    xia = (xxa - 6620 + 2.5) / 5.0
    xio = (xxo + 2.5) / 5.0

    iaa = min(max(round(xia - R2), 1), 237)
    iay = min(max(round(xia + R2), 1), 237) + 1
    ioa = min(max(round(xio - R2), 1), 144)
    ioy = min(max(round(xio + R2), 1), 143) + 1

    ylm, xlm = 0.0, 0.0
    ysm, xsm = 0.0, 0.0

    for xi in range(iaa, iay):
        for xj in range(ioa, ioy):
            e = np.sqrt((xia - xi) ** 2 + (xio - xj) ** 2)
            y = merja[xi - 1, xj - 1] - 48.0
            if e <= R1:
                al = 1.0 - e / R1
                ylm += al
                if 0.0 <= y < 10.0:
                    xlm += y * al
            if e <= R2:
                as_ = 1.0 - e / R2
                ysm += as_
                if 17.0 <= y <= 26.0:
                    xsm += (y - 17.0) * as_

    return (
        xlm / ylm * 100.0 / 9.0 if ylm > 0 else 0.0,
        xsm / ysm * 100.0 / 9.0 if ysm > 0 else 0.0
    )

GRAD_P = np.array([
    -3.738,-.5146,-.5724,-.4210,.09886,.2642,
    -4.286,-.4676,-.5372,-.4000,.1326,.1659,
    -1.73,-.4458,-.3680,-.3290,.1787,.0465,
    4.128,-.4941,-.0719,-.4840,.08718,-.1224,
    10.727,-.5363,.01806,-.5220,.02329,-.2872,
    14.7805,-.4269,.1981,-.4560,.03220,-.2214,
    17.607,-.3270,.1133,-.3530,.08092,-.05788,
    16.098,-.3720,.0523,-.4040,.1599,.09754,
    11.4878,-.3967,-.083,-.452,.2147,.1763,
    6.620,-.5155,-.1968,-.4110,.2036,.2136,
    2.7711,-.5639,-.2843,-.532,.17896,.2236,
    -.287,-.5482,-.49119,-.4910,.09899,.25027
], dtype=np.float64)

@njit
def gmalli_p(
    k: int,
    xla: float,
    xlo: float,
    xh: float,
    xj: float,
    xm: float,
) -> float:
    m = 6*k
    return (
        GRAD_P[m]
        + GRAD_P[m+1] * (xla-6500)/100
        + GRAD_P[m+2] * (xlo-60)/80
        + GRAD_P[m+3] * xh/100
        + GRAD_P[m+4] * xj/10
        + GRAD_P[m+5] * xm/10
    )

GRAD_P1 = np.array([
    -3.735,-.5274,-.5652,-.4101,.1104,.2694,-.2976,
    -4.270,-.4556,-.5427,-.4475,.1400,.1588,.1993,
    -1.738,-.4250,-.3731,-.3653,.1662,.0365,.4359,
    4.161,-.4597,-.0889,-.5873,.0914,-.1411,.6590,
    10.751,-.4948,.0058,-.6307,.0191,-.3089,.8176,
    14.831,-.3722,.1702,-.6162,.0380,-.2504,1.0341,
    17.652,-.2675,.0838,-.5134,.0815,-.0884,1.1346,
    16.145,-.3266,.0283,-.5471,.1701,.0732,.8272,
    11.538,-.3658,-.1022,-.5670,.2334,.1587,.5330,
    6.676,-.5025,-.2097,-.4934,.2309,.2045,.1723,
    2.816,-.5538,-.2938,-.6059,.2052,.2161,.1101,
    -.2447,-.5467,-.4968,-.5464,.1272,.2469,-.0651
], dtype=np.float64)

@njit
def gmalli_p1(
    k: int,
    xla: float,
    xlo: float,
    xh: float,
    xj: float,
    xm: float,
    xlc: float,
) -> float:
    m = 7*k
    return (
        GRAD_P1[m]
        + GRAD_P1[m+1] * xla
        + GRAD_P1[m+2] * xlo
        + GRAD_P1[m+3] * xh
        + GRAD_P1[m+4] * xj
        + GRAD_P1[m+5] * xm
        + GRAD_P1[m+6] * xlc
    )

def env(xla: float, xlo: float) -> Tuple[List[int], List[float]]:
    w: List[float] = []
    ie: List[int] = []
    ee = 9999
    iee = -1
    r = 100
    for i in range(len(asemko8110)):
        x, y = asemko8110[i,1:3]
        e = math.sqrt((xla-x)**2 + (xlo-y)**2)
        if e < ee:
            iee, ee = i, e
        if e < r:
            ie.append(i)
            w.append(1-e/r)
    if not w:
        ie.append(iee)
        w.append(1)
    return ie, w

def po(xla: float, xlo: float, data: npt.NDArray,) -> float:
    ie, w = env(xla, xlo)
    w = np.array(w)
    return sum(w * data[ie]) / sum(w)

def aver(xlx: float, xly: float, xlk: float, xlj: float) -> Tuple[List[float], List[float]]:
    temp = np.array([
        [ilmon8110[i,2+j] - gmalli_p(j, *asemko8110[i,1:6]) for j in range(12)]
        for i in range(len(ilmon8110))
    ])
    tempkk = [po(xlx, xly, temp[:,i]) + gmalli_p(i, xlx, xly, xlk, xlj,  0) for i in range(12)]
    rainkk = [po(xlx, xly, ilmon8110[:,14+i]) for i in range(12)]
    return tempkk, rainkk

def icsscu(
    x: List[float],
    f: List[float],
    df: List[float],
    sm: float
) -> Tuple[List[float], npt.NDArray]:
    nx = len(x)
    wk = np.zeros((nx+2, 7))
    c = np.zeros((nx-1, 3))
    f2 = -sm
    h = x[1]-x[0]
    ff = (f[2]-f[1]) / h
    y = [0.0] * nx
    p = 0
    g = 0
    if nx >= 3:
        for i in range(2,nx):
            g = h
            h = x[i]-x[i-1]
            e = ff
            ff = (f[i]-f[i-1])/h
            y[i] = ff - e
            wk[i,3] = (g+h)*2/3
            wk[i,4] = h/3
            wk[i,2] = df[i-2]/g
            wk[i,0] = df[i]/h
            wk[i,1] = -df[i-1]/g - df[i-1]/h
        for i in range(2, nx):
            c[i-1,0] = wk[i,0]**2 + wk[i,1]**2 + wk[i,2]**2
            c[i-1,1] = wk[i,0]*wk[i+1,1] + wk[i,1]*wk[i+1,2]
            c[i-1,2] = wk[i,0]*wk[i+2,2]
    while True:
        if nx >= 3:
            for i in range(2, nx):
                wk[i-1,1] = ff*wk[i-1,0]
                wk[i-2,2] = g*wk[i-2,0]
                wk[i,0] = 1/(p*c[i-1,0]+wk[i,3]-ff*wk[i-1,1]-g*wk[i-2,2])
                wk[i,5] = y[i] - wk[i-1,1]*wk[i-1,5] - wk[i-2,2]*wk[i-2,5]
                ff = p*c[i-1,1] + wk[i,4] - h*wk[i-1,1]
                g = h
                h = c[i-1,2]*p
            for i in range(2, nx):
                j = nx+1-i
                wk[j,5] = wk[j,0]*wk[j,5] - wk[j,1]*wk[j+1,5] - wk[j,2]*wk[j+2,5]
        e, h = 0, 0
        for i in range(1, nx):
            g = h
            h = (wk[i+1,5]-wk[i,5])/(x[i]-x[i-1])
            wk[i,6] = (h-g)*df[i-1]**2
            e += wk[i,6]*(h-g)
        g = -h*df[nx-1]**2
        wk[nx,6] = g
        e -= g*h
        g = f2
        f2 = e*p**2
        if g < f2 < sm:
            ff = 0
            h = (wk[2,6]-wk[1,6])/(x[1]-x[0])
            if nx >= 3:
                for i in range(2, nx):
                    g = h
                    h = (wk[i+1,6]-wk[i,6])/(x[i]-x[i-1])
                    g = h - g - wk[i-1,1]*wk[i-1,0] - wk[i-2,2]*wk[i-2,0]
                    ff += wk[i,0]*g**2
                    wk[i,0] = g
            h = e - p*ff
            if h > 0:
                p += (sm-f2)/((math.sqrt(sm/e)+p)*h)
                continue
        break
    for i in range(nx-1):
        y[i] = f[i] - p*wk[i+1,6]
        c[i,1] = wk[i+1,5]
        wk[i,0] = y[i]
    wk[nx-1,0] = f[nx-1] - p*wk[nx,6]
    y[nx-1] = wk[nx-1,0]
    for i in range(1, nx):
        h = x[i] - x[i-1]
        c[i-1,2] = (wk[i+1,5]-c[i-1,1])/(3*h)
        c[i-1,0] = (wk[i,0]-y[i-1])/h - (h*c[i-1,2]+c[i-1,1])*h
    return y, c # type: ignore

PXP = [0.,31.,59.,90.,120.,151.,181.,212.,243.,273.,304.,334.]
XPP = [*(PXP[i]+(PXP[i+1]-PXP[i])/2 for i in range(11)), 349.5]
DF  = [1.0] * 12
HA  = [2.7, 3.0]

def xls(
    xl: List[float],
    laji: int = 0,
    taso: float = 5.0,
    alr: int = 0,
    ylr: int = 366
) -> float:
    yc, c = icsscu(XPP, xl, DF, 0)
    dy = [0.0] * 12

    j, kk = -1, 0
    for i in range(32, 335):
        if i > XPP[j+1]:
            j += 1
        d = i - XPP[j]
        a = c[j,2]*d**3 + c[j,1]*d**2 + c[j,0]*d + yc[j]
        if i > PXP[kk+1]:
            kk += 1
        dy[kk] += a

    for i in range(1, 11):
        dy[i] /= PXP[i+1]-PXP[i]
        dy[i] -= xl[i]

    yck, ck = icsscu(XPP, dy, DF, 0)
    xal, xlo, xls = 0, 0, 0
    for i in range(alr, ylr):
        if i < 32:
            a = xl[0]
        elif i > 334:
            a = xl[11]
        else:
            jk = -1
            for ka in range(11):
                if XPP[ka] < i <= XPP[ka+1]:
                    jk = ka
            d = i - XPP[jk]
            a = c[jk,2]*d**3 + c[jk,1]*d**2 + c[jk,0]*d + yc[jk]
            b = ck[jk,2]*d**3 + ck[jk,2]*d**2 + ck[jk,0]*d + yck[jk]
            a -= b
        rnn = i/183
        nn = int(rnn)
        e = a - taso
        g0 = e / HA[nn]
        if laji <= 0:
            if abs(g0) < 2:
                ig0 = int(max((g0+3)*100, 1))
                p0 = 0
                for iig in range(1, ig0+1):
                    ga0 = iig/100 - 3
                    p0 += (1/math.sqrt(2*math.pi)) * math.exp(-ga0**2/2) / 100
                g1 = (1/math.sqrt(2*math.pi)) * math.exp(-g0**2/2) / p0
                g = g0 + g1
                xls += p0 * g * HA[nn]
            elif a > taso:
                xls += a - taso
        if a < taso and i < 181:
            xal = i + 5
        if a > taso:
            xlo = i + 5
        if laji == 1:
            xls = xal
        if laji == 2:
            xls = xlo
        if laji == 3:
            xls = xlo - xal
        xal = xls

    return xls

@dataclasses.dataclass
class WeatherInfo:
    temp: List[float]
    rain: List[float]
    dd: int
    lake: float
    sea: float

def ilmanor(X_ykj: float, Y_ykj: float, Z: float) -> WeatherInfo:
    X_ykj -= 3000
    xj, xm = flase(Y_ykj, X_ykj)
    temp, rain = aver(Y_ykj, X_ykj, Z, xj)
    dd = xls(temp)
    return WeatherInfo(
        temp = temp,
        rain = rain,
        dd = round(dd),
        lake = xj / 100,
        sea = xm / 100
    )
