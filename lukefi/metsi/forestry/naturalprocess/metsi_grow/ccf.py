import math
from .coding import SiteTypeVMI, Species, TaxClassReduction
from .kanto import dk, dkjs_small

PP = [2.067, 1.593, 2.218, 1.855]
P = [
    (
        0.0007666,-0.17,-0.4268,-0.003178,-0.003178, 0.03012,
        0.07614,-0.7614, 0.05279, 0.01913, 0.08891, 0.10120, 0.1459,
        -0.3249,-0.03374,-0.35, 0.01252
    ),
    (
        0.0032920,-0.16,-0.1645,-0.020720, 0.002699, 0.01562,
        0.05627,-0.9653, 0.04533, 0.03494, 0.06530,-0.03203,-0.05316,
        -0.4245,-0.06554, 0.00,0.03391,
    ),
    (
        0.00068284, 0.00, 0.0000, 0.000000, 0.000000, 0.00000,
        0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,
    ),
    (
        0.001914, 0.00, 0.0000, 0.000000, 0.000000, 0.00000,
        0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.
    )
]

def ccf(
    d: float,
    f: float,
    spe: Species,
    mty: SiteTypeVMI,
    verlt: TaxClassReduction,
    lake: float,
    sea: float,
    Z: float,
    dd: float
) -> float:
    if spe == Species.CONIFEROUS:
        spe = Species.PINE
    if spe == Species.ASPEN:
        spe = Species.SILVER_BIRCH
    elif spe >= 4:
        spe = Species.DOWNY_BIRCH

    p = P[spe-1]

    y = (
        + p[3]  * int(mty == SiteTypeVMI.OMaT)
        + p[4]  * int(mty == SiteTypeVMI.OMT)
        + p[5]  * int(mty == SiteTypeVMI.VT)
        + p[6]  * int(mty == SiteTypeVMI.CT)
        + p[7]  * int(mty >= SiteTypeVMI.ClT)
        + p[8]  * int(verlt == TaxClassReduction.STONY)
        + p[9]  * int(verlt == TaxClassReduction.WET)
        + p[10] * int(verlt == TaxClassReduction.MOSS)
        + p[11] * lake
        + p[12] * sea
        + p[13]/1000 * Z
        + p[14]/1000000 * dd * Z
        + int(mty >= SiteTypeVMI.ClT) * (p[15] + dd/1000)**p[16]
    )

    c0_1 = (p[0]/1000) * (p[1] + dd/1000)**p[2] * math.exp(y)
    draj = dk(8)
    if dk(d) < draj:
        xn0 = draj**(-PP[spe-1]) / c0_1
        xd0 = -PP[spe-1]*draj**(-PP[spe-1]-1) / c0_1
        xnn = (xn0-xd0*draj)+dk(d)*xd0
    else:
        xnn = dk(d)**(-PP[spe-1]) / c0_1

    if xnn > 0:
        kal = 0.6 if mty == SiteTypeVMI.ROCKY else 1.0
        lak = 0.5 if mty == SiteTypeVMI.MOUNTAIN else 1.0
        return kal * lak * f / xnn
    else:
        return 0

CCFI_PQ = [
    (1135176.769, 2.05509574),
    (302991.4239, 1.55383579),
    (1493184.82,  2.21782048),
    (529087.1965, 1.85449784),
    (529087.1965, 1.85449784),
    (529087.1965, 1.85449784),
    (529087.1965, 1.85449784),
    (1135176.769, 2.05509574),
    (529087.1965, 1.85449784),
]

def ccfidx(spe: Species, f: float, dx: float) -> float:
    p, q = CCFI_PQ[spe-1]
    return f * (dx**q)/p

def ccfi_small(spe: Species, f: float, h: float) -> float:
    return ccfidx(spe, f, dkjs_small(h))

def ccfi_big(spe: Species, f: float, d: float) -> float:
    return ccfidx(spe, f, dk(d))

def ccfi(spe: Species, f: float, d: float, h: float) -> float:
    if h <= 3:
        return ccfi_small(spe, f, h)
    else:
        return ccfi_big(spe, f, d)
