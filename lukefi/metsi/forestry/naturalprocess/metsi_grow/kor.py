import dataclasses
import itertools
import numpy as np
import numpy.typing as npt

def kordecode(c: int) -> float:
    if c == 40: return 44
    if c == 41: return 46
    if c == 42: return 48
    if c == 43 or c == 32: return 0.5
    return float(c) - 48

#       +----------------------+ (Ymax, Xmax)
#       |                      |
#       |                      |
#       |         +-------+    |
#       |         |       |    |
#       | (Y,X) ----> *   |    |
#       |         |       |    |
#       |         +-------+    |
#       |    (Y0,X0)           |
#       |                      |
#       |                      |
# (0,0) +----------------------+
@dataclasses.dataclass
class HMat:
    # target cell
    Y: float
    X: float
    # target cell, relative to _indices_.
    Yrel: float
    Xrel: float
    # height matrix
    mat: npt.NDArray[np.float64]

def hmat(Y_ykj: float, X_ykj: float, r: float = 3.09) -> HMat:
    from .kordata import KORDAT, KORX, KORY, KREC
    X_ykj -= 3000
    xxa = Y_ykj - 1.67/2
    xxo = X_ykj - 1.67/2
    ioa = int(6*(xxo-r)/10-6)
    ioy = int(6*(xxo+r)/10-4)
    w = ioy - ioa + 1
    ireci = int((xxa-r)/10)-663
    if ireci < 0:
        ir = 0
    elif ireci < len(KREC):
        ir = KREC[ireci]-1
    else:
        ir = len(KORX)-1
    ix1 = KORY[ir]
    xia = (xxa-ix1)/1.67
    ik = 0
    xkork = [[0.0]*w for _ in range(6)]
    while True:
        ixx = KORY[ir]
        iyy = KORX[ir]
        m = 6*iyy-5
        lo = min(max(ioa, m), ioy+1)
        hi = min(max(ioa, m+6), ioy+1)
        for mm in range(lo, hi):
            for l in range(6):
                xkork[ik+l][mm-ioa] = 20*kordecode(KORDAT[36*ir+6*l+mm-m]) - 10
        ir += 1
        if ix1 != ixx:
            xkork.extend([0.0]*w for _ in range(6))
            ik += 6
            ix1 = ixx
        if ir >= len(KORY) or ixx > xxa+r:
            break
    return HMat(
        Y = xxa,
        X = xxo,
        Yrel = xia,
        Xrel = 6*xxo/10-5 - ioa,
        mat = np.array(xkork)
    )

def height(hm: HMat, r: float = 3.09) -> float:
    sy2 = (r/1.67)**2
    gko, yl = 0, 0
    mat = hm.mat
    for i, j in itertools.product(range(mat.shape[0]), range(mat.shape[1])):
        e2 = (hm.Yrel-i)**2 + (hm.Xrel-j)**2
        if e2 > sy2:
            continue
        v = mat[i,j]
        if v == 0 and (hm.X > 540 or hm.Y > 7300):
            continue
        gko += v
        yl += 1
    if yl == 0:
        raise ValueError("point out of range")
    return gko/yl

def xkor(Y_ykj: float, X_ykj: float, r: float = 3.09) -> float:
    return height(hmat(Y_ykj, X_ykj, r=r), r=r)
