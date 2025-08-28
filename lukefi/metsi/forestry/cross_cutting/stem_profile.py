import numpy as np
from numba import njit
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.forestry.cross_cutting.taper_curves import TAPER_CURVES


@njit(fastmath=True)
def _taper_curve_correction(d: float, h: int, sp: int) -> np.ndarray:
    dh = d / (h - 1.3)
    dh2 = dh * dh
    dl = np.log(d)
    hl = np.log(h)
    d2 = d * d

    if sp == 1:  # pine
        t1 = 1.100553
        t4 = 0.8585458
        t7 = 0.5442665

        y1 = 0.26222 - 0.0016245 * d + 0.010074 * h + 0.06273 * dh - 0.011971 * dh2 - 0.15496 * hl - 0.45333 / h
        y4 = -0.38383 - 0.0055445 * h - 0.014121 * dl + 0.17496 * hl + 0.62221 / h
        y7 = -0.179 + 0.037116 * dh - 0.12667 * dl + 0.18974 * hl

    elif sp == 2:  # spruce
        t1 = 1.0814409
        t4 = 0.8409653
        t7 = 0.4999158

        y1 = -0.003133 * d + 0.01172 * h + 0.48952 * dh - 0.078688 * dh2 - 0.31296 * dl + 0.13242 * hl - 1.2967 / h
        y4 = -0.0065534 * d + 0.011587 * h - 0.054213 * dh + 0.011557 * dh2 + 0.12598 / h
        y7 = 0.084893 - 0.0064871 * d + 0.012711 * h - 0.10287 * dh + 0.026841 * dh2 - 0.01932 * dl

    elif sp == 3:  # birch
        t1 = 1.084544
        t4 = 0.8417135
        t7 = 0.4577622

        y1 = 0.59848 + 0.011356 * d - 0.49612 * dl + 0.46137 * hl - 0.92116 / dh + 0.25182 / dh2 - 0.00019947 * d2
        y4 = -0.96443 + 0.011401 * d + 0.13870 * dl + 1.5003 / h + 0.57278 / dh - 0.18735 / dh2 - 0.00026 * d2
        y7 = -2.1147 + 0.79368 * dl - 0.51810 * hl + 2.9061 / h + 1.6811 / dh - 0.40778 / dh2 - 0.00011148 * d2

    elif sp == 4:  # alnus
        t1 = 1.108743
        t4 = 0.8186044
        t7 = 0.4682397

        y1 = -1.46153 + 0.0487415 * d + 0.663667 * dl - 0.827114 * hl - \
            0.00106612 * d2 + 1.87966 / h + 1.85706 / dh - 0.467842 / dh2
        y4 = -1.24788 - 0.0218693 * dh2 + 0.496483 * dl - 0.291413 * hl + 1.92579 / h + 0.863274 / dh - 0.183220 / dh2
        y7 = -0.478730 - 0.104679 * dh + 0.151028 * dl + 0.882010 / h + 0.178386 / dh

    else:
        raise MetsiException(f"Unsupported species code '{sp}'")

    # Clamp and preserve sign
    def clamp(y):
        y_clamp = min(abs(y), 0.1)
        if y_clamp * y < 0:
            y_clamp = -y_clamp
        return y_clamp

    y1t = clamp(y1)
    y4t = clamp(y4)
    y7t = clamp(y7)

    p = np.zeros(5)
    p[0] = 0.9
    p[1] = 0.6
    p[2] = t1 / (t1 + y1t) * (t4 + y4t) - t4
    p[3] = 0.3
    p[4] = t1 / (t1 + y1t) * (t7 + y7t) - t7

    return p


@njit(fastmath=True)
def _cpoly3(p: np.ndarray) -> np.ndarray:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    con1 = p[2] / (p[1] * (p[1] - p[0]))
    con2 = p[4] / (p[3] * (p[3] - p[0]))

    b = np.zeros(3)
    b[2] = (con1 - con2) / (p[1] - p[3])
    b[1] = con1 - b[2] * (p[0] + p[1])
    b[0] = p[0] * (p[1] * b[2] - con1)

    return b


@njit(fastmath=True)
def _dhat(h: np.ndarray, height: int, coef: np.ndarray) -> np.ndarray:
    n = len(h)
    dhat = np.zeros(n)

    for i in range(n):
        x = (height - h[i]) / height
        x2 = x * x
        x3 = x2 * x
        x5 = x2 * x3
        x8 = x5 * x3
        x13 = x5 * x8
        x21 = x8 * x13
        x34 = x13 * x21

        dhat[i] = (
            x * coef[0] +
            x2 * coef[1] +
            x3 * coef[2] +
            x5 * coef[3] +
            x8 * coef[4] +
            x13 * coef[5] +
            x21 * coef[6] +
            x34 * coef[7]
        )

    return dhat


@njit(fastmath=True)
def _crkt(h: float, height: int, coef: np.ndarray) -> float:
    x = (height - h) / height

    x2 = x * x
    x3 = x2 * x
    x5 = x2 * x3
    x8 = x5 * x3
    x13 = x5 * x8
    x21 = x8 * x13
    x34 = x13 * x21

    return (
        x * coef[0] +
        x2 * coef[1] +
        x3 * coef[2] +
        x5 * coef[3] +
        x8 * coef[4] +
        x13 * coef[5] +
        x21 * coef[6] +
        x34 * coef[7]
    )


@njit(fastmath=True)
def _ghat(h: float, height: int, coef: np.ndarray) -> float:
    x = (height - h) / height
    x2 = x * x
    x3 = x2 * x
    x5 = x2 * x3
    x8 = x5 * x3
    x13 = x5 * x8
    x21 = x8 * x13
    x34 = x13 * x21

    d = (
        x * coef[0] +
        x2 * coef[1] +
        x3 * coef[2] +
        x5 * coef[3] +
        x8 * coef[4] +
        x13 * coef[5] +
        x21 * coef[6] +
        x34 * coef[7]
    )

    d = d / 100.0
    return (d * d) * np.pi / 4.0

@njit(fastmath=True)
def _ghat_integrated(h_: float, height: int, coef: np.ndarray) -> float:
    x = (height - h_) / height
    # h = -(x * height - height) = height - x * height
    # dh / dx = -height
    x2 = x * x
    x3 = x * x2
    x4 = x2 * x2
    x5 = x2 * x3
    x6 = x3 * x3
    x7 = x3 * x4
    x8 = x4 * x4
    x9 = x4 * x5
    x10 = x5 * x5
    x11 = x5 * x6
    x12 = x6 * x6
    x14 = x7 * x7
    x15 = x7 * x8
    x16 = x8 * x8
    x17 = x8 * x9
    x19 = x9 * x10
    x22 = x11 * x11
    x23 = x11 * x12
    x24 = x12 * x12
    x25 = x14 * x11
    x27 = x11 * x16
    x30 = x15 * x15
    x35 = x23 * x12
    x36 = x17 * x19
    x37 = x15 * x22
    x38 = x19 * x19
    x40 = x17 * x23
    x43 = x19 * x24
    x48 = x24 * x24
    x56 = x37 * x19
    x69 = x23 * x23 * x23

    a = coef[0]
    b = coef[1]
    c = coef[2]
    d = coef[3]
    e = coef[4]
    f = coef[5]
    g = coef[6]
    h = coef[7]

    return -height * np.pi / 40000 * ((a * a) / 3 * x3 +
                                      (a * b) / 2 * x4 +
                                      (2 * a * c + b * b) / 5 * x5 +
                                      (b * c) / 3 * x6 +
                                      (2 * a * d + c * c) / 7 * x7 +
                                      (b * d) / 4 * x8 +
                                      (c * d) * 2 / 9 * x9 +
                                      (a * e) / 5 * x10 +
                                      (2 * b * e + d * d) / 11 * x11 +
                                      (c * e) / 6 * x12 +
                                      (d * e) / 7 * x14 +
                                      (a * f) * 2 / 15 * x15 +
                                      (b * f) / 8 * x16 +
                                      (2 * c * f + e * e) / 17 * x17 +
                                      (d * f) * 2 / 19 * x19 +
                                      (e * f) / 11 * x22 +
                                      (a * g) * 2 / 23 * x23 +
                                      (b * g) / 12 * x24 +
                                      (c * g) * 2 / 25 * x25 +
                                      (2 * d * g + f * f) / 27 * x27 +
                                      (e * g) / 15 * x30 +
                                      (f * g) * 2 / 35 * x35 +
                                      (a * h) / 18 * x36 +
                                      (b * h) * 2 / 37 * x37 +
                                      (c * h) / 19 * x38 +
                                      (d * h) / 20 * x40 +
                                      (2 * e * h + g * g) / 43 * x43 +
                                      (f * h) / 24 * x48 +
                                      (g * h) / 28 * x56 +
                                      (h * h) / 69 * x69)

@njit
def _volume(hkanto: float, height: int, coeff: np.ndarray):
    step = 0.1
    n_steps = int((height - hkanto) / step)
    h = np.linspace(hkanto, hkanto + n_steps * step, n_steps + 1)
    if h[-1] < height:
        # add one last segment to reach full height
        h = np.concatenate((h, np.array([height])))

    v_piece = np.zeros(len(h) - 1)
    d_piece = _dhat(h[1:], height, coeff)  # make sure _dhat_fast is @njit

    for j, _ in enumerate(v_piece):
        x0 = h[j]
        x1 = h[j+1]

        v_piece[j] = _ghat_integrated(x1, height, coeff) - _ghat_integrated(x0, height, coeff)

    h_piece = h[1:]
    v_cum = np.cumsum(v_piece)

    return (v_cum, d_piece, h_piece)


SPECIES_FOR_STEM_PROFILE = {
    "pine": 1,
    "spruce": 2,
    "birch": 3,
    "alnus": 4
}


def create_tree_stem_profile(species_string: str, dbh: float, height: int, n: int,
                             hkanto: float = 0.1) -> np.ndarray:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    taper_curve = TAPER_CURVES.get(species_string, TAPER_CURVES["birch"])  # fallback default
    coefs = np.array(list(taper_curve["climbed"].values()))

    species_code = SPECIES_FOR_STEM_PROFILE.get(
        species_string, SPECIES_FOR_STEM_PROFILE["birch"])  # default to "birch" → code 3

    p = _taper_curve_correction(dbh, height, species_code)

    b = _cpoly3(p)

    coefnew = coefs.copy()
    for i in range(3):
        coefnew[i] += b[i]

    hx = 1.3
    c = _crkt(hx, height, coefnew)
    d20 = dbh / c

    coefnew = coefnew * d20

    v_cum, d_piece, h_piece = _volume(hkanto, height, coefnew)

    T = np.empty((n, 3))  # pylint: disable=invalid-name
    T[:, 0] = d_piece * 10
    T[:, 1] = h_piece
    T[:, 2] = v_cum

    return T
