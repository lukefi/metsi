from lukefi.metsi.forestry.cross_cutting.taper_curves import TAPER_CURVES
import numpy as np
from scipy import integrate

def _taper_curve_correction(d: float, h: int, sp: str) -> np.ndarray:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    dh = d / (h-1.3)
    dh2 = dh**2
    dl = np.log(d)
    hl = np.log(h)
    d2 = d**2

    if sp=="pine":
        t1 = 1.100553
        t4 = 0.8585458
        t7 = 0.5442665
        
        y1 = (0.26222 - 0.0016245*d + 0.010074*h + 0.06273*dh -
        0.011971*dh2 - 0.15496*hl - 0.45333/h)
        y4 = -0.38383 - 0.0055445*h - 0.014121*dl + 0.17496*hl + 0.62221/h
        y7 = -0.179 + 0.037116*dh - 0.12667*dl + 0.18974*hl
        
        
    if sp=="spruce":
        t1 = 1.0814409
        t4 = 0.8409653
        t7 = 0.4999158
        #
        y1 = (-0.003133*d + 0.01172*h + 0.48952*dh - 0.078688*dh2 -
        0.31296*dl + 0.13242*hl - 1.2967/h)
        y4 = (-0.0065534*d + 0.011587*h - 0.054213*dh + 0.011557*dh2 +
        0.12598/h)
        y7 = (0.084893 - 0.0064871*d + 0.012711*h - 0.10287*dh +
        0.026841*dh2 - 0.01932*dl)

    if sp=="birch":
        t1 = 1.084544
        t4 = 0.8417135
        t7 = 0.4577622
        
        y1 = (0.59848 + 0.011356*d - 0.49612*dl + 0.46137*hl -
            0.92116/dh + 0.25182/dh2 - 0.00019947*d2)
        y4 = (-0.96443 + 0.011401*d + 0.13870*dl + 1.5003/h +
            0.57278/dh - 0.18735/dh2 - 0.00026*d2)
        y7 = (-2.1147 + 0.79368*dl - 0.51810*hl + 2.9061/h +
            1.6811/dh - 0.40778/dh2 - 0.00011148*d2)
    
    if sp=="alnus":
        t1 = 1.108743
        t4 = 0.8186044
        t7 = 0.4682397
        #
        y1 = (-1.46153 + 0.0487415*d + 0.663667*dl - 0.827114*hl -
        0.00106612*d2 + 1.87966/h + 1.85706/dh - 0.467842/dh2)
        y4 = (-1.24788 - 0.0218693*dh2 + 0.496483*dl - 0.291413*hl +
        1.92579/h + 0.863274/dh - 0.183220/dh2)
        y7 = (-0.478730 - 0.104679*dh + 0.151028*dl + 0.882010/h +
        0.178386/dh)

    y1t = min(abs(y1),0.1)

    if np.sign(y1t) != np.sign(y1):
        y1t = y1t * -1

    y4t = min(abs(y4),0.1)

    if np.sign(y4t) != np.sign(y4):
        y4t = y4t * -1

    y7t = min(abs(y7),0.1)

    if np.sign(y7t)!=np.sign(y7):
        y7t = y7t * -1

    p = np.zeros(5)
    p[0] = 0.9
    p[1] = 0.6
    p[2] = t1/(t1+y1) * (t4+y4) - t4
    p[3] = 0.3
    p[4] = t1/(t1+y1) * (t7+y7) - t7

    return p

def _cpoly3(p: np.ndarray) -> np.ndarray:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    con1 = p[2] / (p[1] * (p[1]-p[0]))
    con2 = p[4] / (p[3] * (p[3]-p[0]))

    b = np.zeros(3)
    b[2] = (con1-con2) / (p[1]-p[3])
    b[1] = con1 - b[2] * (p[0]+p[1])
    b[0] = p[0] * (p[1]*b[2] - con1)

    return b

def _dhat(h: np.ndarray, height: int, coef: np.ndarray) -> np.ndarray:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    x = (height-h)/height
    dhat = (x*coef[0]+x**2*coef[1]+x**3*coef[2]+x**5*coef[3]+
        x**8*coef[4]+x**13*coef[5]+x**21*coef[6]+x**34*coef[7])

    return dhat

def _crkt(h: float, height: int, coef: np.ndarray) -> float:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    x = (height-h)/height

    crkt = (x*coef[0]+x**2*coef[1]+x**3*coef[2]+x**5*coef[3]+
        x**8*coef[4]+x**13*coef[5]+x**21*coef[6]+x**34*coef[7])

    return crkt

def _ghat(h: float, height: int, coef: np.ndarray) -> float:
    """
    This function has been ported from, and should be updated according to, the R implementation
    """
    x = (height-h)/height
    d = (x*coef[0]+x**2*coef[1]+x**3*coef[2]+x**5*coef[3]+x**8*coef[4]+x**13*coef[5]+x**21*coef[6]+x**34*coef[7])
    d = d/100
    return (d**2)*np.pi/4

def _volume(hkanto: float, dbh: float, height: int, coeff: np.ndarray) -> tuple[np.ndarray]:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    h = np.arange(hkanto, height, 0.1) # len=259 whereas in R it's 250 (arange is exclusive on the upper bound)
    if h[-1] < height: #this will be true here, but not in R
        h = np.append(h, height)
    
    v_piece = np.zeros(len(h)-1)
    d_piece = _dhat(h[1:], height, coeff)

    for j in range(len(v_piece)):
        y, abserr = integrate.quad(_ghat, h[j], h[j+1], args=(height, coeff))
        v_piece[j] = y
    
    h_piece = h[1:]
    v_cum = np.cumsum(v_piece)

    return (v_cum, d_piece, h_piece)

def create_tree_stem_profile(species_string: str, dbh: float, height: int, n: int, hkanto: float=0.1, div: int=10) -> np.ndarray:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    taper_curve = TAPER_CURVES.get(species_string, "birch")
    coefs = np.array(list(taper_curve["climbed"].values()))

    p = _taper_curve_correction(dbh, height, species_string)

    b = _cpoly3(p)

    coefnew = coefs

    for i in range(3):
        coefnew[i] = coefs[i] + b[i]

    hx = 1.3
    c = _crkt(hx, height, coefnew)
    d20 = dbh/c

    coefnew = coefnew * d20

    v_cum, d_piece, h_piece = _volume(hkanto, dbh, height, coefnew)

    T = np.empty((n, 3))
    T[:, 0] = d_piece * 10
    T[:, 1] = h_piece
    T[:, 2] = v_cum

    return T





