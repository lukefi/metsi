import dataclasses
import math
from typing import List, Optional
from .coding import Origin, SiteTypeVMI, SoilCategoryVMI, SoilPrep, Species, TaxClassReduction

def hvalta_manty(
    t: float,
    mty: SiteTypeVMI,
    snt: Origin,
    dd: float,
    verlt: TaxClassReduction
) -> float:
    plnhd = (
        -3.54554
        - 8.33716  * t**(-0.5)
        + 1.039037 * math.log(dd)
        + 0.428068 * int(snt == Origin.PLANTED) * 1/math.sqrt(t)
        + 0.300919 * int(snt == Origin.SEEDED) * 1/math.sqrt(t)
        + 0.242263 * int(mty <= SiteTypeVMI.OMT)
        + 0.112042 * int(mty == SiteTypeVMI.MT)
        - 0.15247  * int(mty == SiteTypeVMI.CT)
        - 0.26735  * int(mty >= SiteTypeVMI.ClT)
        - 0.04337  * int(verlt == TaxClassReduction.WET)
        - 0.17154  * int(verlt in (TaxClassReduction.STONY, TaxClassReduction.MOSS))
        - 0.1      * int(mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mty >= SiteTypeVMI.MOUNTAIN)
    )
    return math.exp(plnhd+.03810/2)

def hvalta_kuusi(
    t: float,
    mty: SiteTypeVMI,
    snt: Origin,
    dd: float,
    verlt: TaxClassReduction
) -> float:
    plnhd = (
        -1.84155
        - 0.54546 * math.log(t)
        - 91.1669 * 1/(t+10)
        + 1.1676  * math.log(dd)
        + 0.160   * int(mty <= SiteTypeVMI.OMT)
        - 0.272   * int(mty >= SiteTypeVMI.VT)
        - 0.075   * int(verlt == TaxClassReduction.WET)
        - 0.10    * int(verlt in (TaxClassReduction.STONY, TaxClassReduction.MOSS))
        + 0.047   * int(snt == Origin.PLANTED)
        - 0.2     * int(mty >= SiteTypeVMI.CT)
        - 0.1     * int(mty >= SiteTypeVMI.ClT)
        - 0.1     * int(mty >= SiteTypeVMI.ROCKY)
        - 0.1     * int(mty >= SiteTypeVMI.MOUNTAIN)
    )
    return math.exp(plnhd+.031977/2)

def hvalta_lehti(
    spe: Species,
    t: float,
    mty: SiteTypeVMI,
    snt: Origin,
    dd: float,
    verlt: TaxClassReduction
) -> float:
    plnhd = (
        -4.02488
        - 7.58258  * 1/math.sqrt(t)
        + 1.137578 * math.log(dd)
        - 0.16127  * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        + 0.077555 * int(mty <= SiteTypeVMI.OMT)
        - 0.25924  * int(mty >= SiteTypeVMI.VT)
        - 0.1      * int(verlt == TaxClassReduction.WET)
        - 0.05     * int(verlt in (TaxClassReduction.STONY, TaxClassReduction.MOSS))
        - 0.1      * int(mty >= SiteTypeVMI.CT)
        - 0.1      * int(mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mty >= SiteTypeVMI.MOUNTAIN)
        + 0.4      * int(snt >= Origin.SEEDED) * 1/math.sqrt(t)
    )
    return math.exp(plnhd+.022461/2)

def hvalta(
    spe: Species,
    t: float,
    mty: SiteTypeVMI,
    snt: Origin,
    dd: float,
    verlt: TaxClassReduction
) -> float:
    if spe in (Species.PINE, Species.CONIFEROUS):
        return hvalta_manty(t, mty, snt, dd, verlt)
    elif spe == Species.SPRUCE:
        return hvalta_kuusi(t, mty, snt, dd, verlt)
    else:
        return hvalta_lehti(spe, t, mty, snt, dd, verlt)

def agekri_empty(
    spe: Species,
    mty: SiteTypeVMI,
    snt: Origin,
    dd: float,
    verlt: TaxClassReduction,
    hlim: float = 8.0,
    alim: float = 50.0,
    a: float = 2.0
) -> float:
    while a < alim and hvalta(spe, a+1, mty, snt, dd, verlt) < hlim:
        a += 1
    return a

MTAPAP = [25.,30.,25.,25.,15.,25.]
SLOPMT = [5.0,5.0,10.0,15.0,25.0,25.0,25.0,25.0]
CERMT = [
    (0.4, 0.4, 0.5, 0.6, 0.8, 0.9, 1.0, 1.0),
    (0.6, 0.6, 0.6, 0.6, 0.8, 0.9, 1.0, 1.0),
    (0.6, 0.6, 0.6, 0.6, 0.8, 0.9, 1.0, 1.0)
]

def mpkmmannut(
    mty: SiteTypeVMI,
    alr: SoilCategoryVMI,
    dd: float,
    muok: Optional[SoilPrep],
    t_muok: float
) -> float:
    t = min(max(t_muok, 0), 10)
    xos = -t**2
    xnim = SLOPMT[mty-1] * (1400.0/dd)**1.25
    tu = CERMT[min(alr-1,2)][mty-1]
    if (not muok) or muok == SoilPrep.NONE:
        return tu * (tu + (1-tu)*math.exp(xos/xnim))
    else:
        return (tu + (1-tu)*math.exp(xos/xnim)) * 299.*MTAPAP[muok-1]/5415

def casc(
    ftot: float,
    snt: Origin,
    G_seed: float,
    f_vilj: float,
    violet: float
) -> float:
    if ftot == 0:
        return 0
    casu = 1 - math.exp((
        -2181.0936
        - 26.9142 * int(snt == Origin.NATURAL)
        - 200.9218 * int(snt >= Origin.SEEDED)
    ) / ftot)
    if snt >= Origin.SEEDED and f_vilj > 0:
        casu **= math.exp(-(f_vilj-violet)/(ftot**0.95))
    if G_seed > 15:
        casu *= 0.75
    return ftot * casu

PLRIV_KANGAS = [
    (1,2,3,4,6,6,6,1,6),
    (1,2,3,4,6,6,6,1,6),
    (1,7,3,4,6,6,6,1,6),
    (9,9,11,11,6,6,6,9,6),
    (12,12,12,12,12,12,12,12,12),
    (12,12,12,12,12,12,12,12,12),
    (14,14,14,14,14,14,14,14,14),
    (14,14,14,14,14,14,14,14,14),
]

PLRIV_SUO = [
    (1,2,3,5,6,6,6,1,6),
    (1,2,3,5,6,6,6,1,6),
    (1,8,3,5,6,6,6,1,6),
    (10,10,11,11,6,6,6,10,6),
    (13,13,13,13,13,13,13,13,13),
    (13,13,13,13,13,13,13,13,13),
    (14,14,14,14,14,14,14,14,14),
    (14,14,14,14,14,14,14,14,14),
]

def plriv(
    spe: Species,
    mty: SiteTypeVMI,
    alr: SoilCategoryVMI
) -> int:
    if alr == SoilCategoryVMI.MINERAL:
        return PLRIV_KANGAS[mty-1][spe-1]-1
    else:
        return PLRIV_SUO[mty-1][spe-1]-1

PLSKAS_LUONT = [
    (0.7930,0.1240,0.0320,0.0510,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.0130,0.8552,0.0348,0.0922,0.0013,0.0030,0.0004,0.0000,0.0000),
    (0.0744,0.1110,0.7142,0.0924,0.0031,0.0025,0.0000,0.0000,0.0025),
    (0.0340,0.1021,0.0563,0.7691,0.0252,0.0118,0.0000,0.0000,0.0015),
    (0.0620,0.0965,0.0120,0.8222,0.0000,0.0021,0.0042,0.0000,0.0010),
    (0.0133,0.0307,0.0467,0.0707,0.2653,0.4240,0.0107,0.0000,0.1387),
    (0.0774,0.8236,0.0396,0.0561,0.0015,0.0015,0.0002,0.0000,0.0000),
    (0.0342,0.8449,0.0037,0.1171,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9128,0.0519,0.0142,0.0210,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.8913,0.0495,0.0012,0.0579,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.2018,0.0371,0.0564,0.7047,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9754,0.0040,0.0064,0.0141,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9777,0.0012,0.0002,0.0209,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9144,0.0367,0.0272,0.0122,0.0095,0.0000,0.0000,0.0000,0.0000)
]

PLSKAS_VILJ = [
    (0.8252,0.0704,0.0494,0.0419,0.0000,0.0000,0.0000,0.0132,0.0000),
    (0.0162,0.8880,0.0552,0.0391,0.0007,0.0009,0.0000,0.0000,0.0000),
    (0.0338,0.0375,0.8889,0.0348,0.0043,0.0003,0.0000,0.0000,0.0005),
    (0.0000,0.0000,0.1029,0.8971,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.0000,0.0000,0.0000,0.0000,1.0000,0.0000,0.0000,0.0000,0.0000),
    (0.0000,0.0420,0.0000,0.0000,0.3631,0.5803,0.0146,0.0000,0.0000),
    (0.0631,0.8474,0.0592,0.0286,0.0000,0.0017,0.0000,0.0000,0.0000),
    (0.0400,0.8629,0.0114,0.0857,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9295,0.0273,0.0246,0.0184,0.0001,0.0000,0.0000,0.0000,0.0000),
    (0.8773,0.0307,0.0000,0.0920,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.2308,0.0000,0.0000,0.7692,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9982,0.0000,0.0018,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.9696,0.0000,0.0000,0.0304,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.8929,0.0536,0.0536,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000)
]

def ykask(
    tspe: Species,
    mty: SiteTypeVMI,
    alr: SoilCategoryVMI,
    snt: Origin
) -> List[float]:
    iplri = plriv(tspe, mty, alr)
    if snt == Origin.NATURAL:
        return list(PLSKAS_LUONT[iplri])
    else:
        return list(PLSKAS_VILJ[iplri])

@dataclasses.dataclass
class TaimiSync:
    f: float
    y: List[float]
    ykas: List[float]

def ysync(
    tspe: Species,
    ftot: float,
    y: List[float],
    fkas: float,
    ykas: List[float]
) -> TaimiSync:
    if y[tspe-1] < 0.3:
        yc = 0.7 / (1-y[tspe-1])
        y = [yy*yc if i != tspe-1 else 0.3*yy for i,yy in enumerate(y)]

    if ykas[tspe-1] < 0.5:
        ykc = 0.5 / (1-ykas[tspe-1])
        ykas = [yy*ykc if i != tspe-1 else 0.5*yy for i,yy in enumerate(ykas)]

    ctpaa = ftot * y[tspe-1]
    ckaspaa = fkas * ykas[tspe-1]
    if ckaspaa > ctpaa:
        yc = (1-(ckaspaa/ftot))/(1-y[tspe-1])
        y = [yy*yc if i != tspe-1 else ckaspaa/ftot for i,yy in enumerate(y)]

    tn = [yy*ftot for yy in y]
    tk = [yy*fkas for yy in ykas]
    for i in range(len(y)):
        if tk[i] > tn[i]:
            ftot += tk[i] - tn[i]
            tn[i] = tk[i]

    if ftot > 0:
        y = [f/ftot for f in tn]
    else:
        y = [0.0]*len(y)

    return TaimiSync(f=ftot, y=y, ykas=ykas)

NLUONT = [
    (
        (7332,5992,11435,11635,16156,15994,8955,5064,7504),
        (8022,9057,16478,12592,16681,16456,14765,6634,13989),
        (7250,8175,11570,7332,16991,9713,6634,5710,8022),
        (6076,4494,5875,5903,9647,5167,5167,4817,6374),
        (4625,3569,4447,3076,6974,4230,4230,3752,5271),
        (4477,2981,3641,2441,5486,3498,3498,3498,4188),
        (4098,2515,2807,2208,3984,2779,2779,3262,3134),
        (1998,1998,1998,1998,1998,1998,1998,1604,1998)
    ),
    (
        (7864,9344,9997,9164,7332,7332,7332,6248,7332),
        (10183,10549,27846,12877,10199,10199,10199,7631,11968),
        (10984,10451,23587,17678,13095,13095,13095,8955,13095),
        (15560,9624,18215,11902,5710,5710,5710,11384,5710),
        (11499,7480,13905,8866,4447,4447,4447,9228,4447),
        (8250,5636,10000,6500,3250,3250,3250,6600,3250),
        (5000,3682,6000,4286,2143,2143,2143,4000,2143),
        (2000,2000,2000,2000,1000,1000,1000,1600,1000)
    ),
    (
        (3000,3000,4800,6000,4800,4800,4800,2400,4800),
        (4428,5000,5886,7412,5886,5886,5886,3437,5886),
        (7245,7394,9600,12104,9600,9600,9600,5972,9600),
        (5498,12708,11355,14204,7097,7097,7097,4542,7097),
        (4447,10471,9350,11731,5844,5844,5844,3530,5844),
        (4017,7765,7850,8323,4162,4162,4162,3072,4162),
        (2900,4824,4700,5226,2613,2613,2613,2320,2613),
        (2000,2000,2000,2000,1000,1000,1000,1600,1000)
    )
]

NVILJ = [
    (
        (5772,8021,3124,4722,3200,3200,3200,3197,3200),
        (8891,8444,7341,8267,6600,6600,6600,8778,6600),
        (7795,9038,8320,10991,8266,8266,8266,7611,8266),
        (6490,7000,7083,8900,4450,4450,4450,6503,4450),
        (4519,5591,5917,7200,3600,3600,3600,5208,3600),
        (3545,4409,4625,5400,2700,2700,2700,4000,2700),
        (2976,3128,3292,3650,1825,1825,1825,2708,1825),
        (2000,2000,2000,2000,1000,1000,1000,1500,1000),
    ),
    (
        (8604,2926,1588,1806,1334,1334,1334,3000,1334),
        (12232,8611,7452,9701,10400,10400,10400,12967,10400),
        (14132,9438,6664,8667,6934,6934,6934,9400,6934),
        (15233,8000,5645,7063,3532,3532,3532,8300,3532),
        (11461,6500,4774,5750,2875,2875,2875,7000,2875),
        (8308,5000,3806,4500,2250,2250,2250,5600,2250),
        (5154,3500,2903,3250,1625,1625,2625,4250,1625),
        (2000,2000,2000,2000,1000,1000,1000,3000,1000),
    ),
    (
        (3000,3000,1600,1667,1334,1334,1334,3000,1334),
        (8188,8224,6333,13000,10400,10400,10400,10000,10400),
        (13233,7333,6500,8667,6934,6934,6934,9400,6934),
        (10444,6417,5645,7063,3532,3532,3532,8300,3532),
        (6000,5292,4774,5750,2875,2875,2875,7000,2875),
        (4438,4167,3839,4500,2250,2250,2250,5600,2250),
        (3250,3042,2903,3250,1625,1625,1625,4250,1625),
        (2000,2000,2000,2000,1000,1000,1000,3000,1000)
    )
]

PLSTOT_LUONT = [
    (0.3423,0.0828,0.0353,0.4633,0.0078,0.0297,0.0297,0.0000,0.0092),
    (0.0064,0.3582,0.0208,0.3075,0.0339,0.0687,0.0687,0.0000,0.1359),
    (0.0138,0.0211,0.7204,0.1808,0.0355,0.0117,0.0117,0.0000,0.0050),
    (0.0293,0.0557,0.0041,0.7587,0.0750,0.0147,0.0147,0.0000,0.0478),
    (0.0217,0.0466,0.0027,0.8869,0.0081,0.0128,0.0128,0.0000,0.0085),
    (0.0047,0.0075,0.0487,0.0648,0.1925,0.4891,0.0500,0.0003,0.1424),
    (0.0181,0.4796,0.0556,0.2626,0.1051,0.0161,0.0161,0.0000,0.0468),
    (0.0845,0.3775,0.0315,0.4717,0.0026,0.0114,0.0114,0.0005,0.0090),
    (0.5581,0.1041,0.0573,0.1982,0.0305,0.0080,0.0080,0.0007,0.0351),
    (0.4823,0.0576,0.0225,0.4316,0.0019,0.0018,0.0018,0.0005,0.0000),
    (0.0411,0.0288,0.0026,0.9018,0.0052,0.0020,0.0020,0.0000,0.0165),
    (0.9148,0.0347,0.0045,0.0395,0.0000,0.0033,0.0033,0.0000,0.0000),
    (0.7273,0.0061,0.0050,0.2615,0.0000,0.0001,0.0001,0.0000,0.0000),
    (0.4900,0.1507,0.0969,0.0854,0.1056,0.0000,0.0000,0.0078,0.0636),
]

PLSTOT_VILJ = [
    (0.3957,0.0643,0.1010,0.3232,0.0347,0.0188,0.0188,0.0112,0.0323),
    (0.0164,0.2135,0.0192,0.1525,0.0601,0.1877,0.1877,0.0069,0.1560),
    (0.0032,0.0286,0.6608,0.0997,0.1521,0.0081,0.0081,0.0000,0.0395),
    (0.0000,0.0000,0.0108,0.7715,0.2177,0.0000,0.0000,0.0000,0.0000),
    (0.0000,0.0000,0.0000,0.9032,0.0000,0.0484,0.0484,0.0000,0.0000),
    (0.0000,0.0115,0.0000,0.0000,0.6763,0.2622,0.0500,0.0000,0.0000),
    (0.0268,0.3998,0.0147,0.1753,0.0160,0.0576,0.0576,0.0000,0.2522),
    (0.1117,0.1140,0.0037,0.7551,0.0000,0.0077,0.0077,0.0000,0.0000),
    (0.6104,0.0518,0.0549,0.2006,0.0398,0.0124,0.0124,0.0001,0.0177),
    (0.4300,0.0153,0.0000,0.5547,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.2542,0.0000,0.0000,0.4916,0.2542,0.0000,0.0000,0.0000,0.0000),
    (0.9948,0.0000,0.0052,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.4378,0.0000,0.0000,0.5622,0.0000,0.0000,0.0000,0.0000,0.0000),
    (0.3003,0.1095,0.0975,0.0000,0.0000,0.0000,0.0000,0.0000,0.4927)
]

RMAA = [1.0, 0.5, 0.05, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]

def plsx_y(
    tspe: Species,
    mty: SiteTypeVMI,
    alr: SoilCategoryVMI,
    snt: Origin
) -> List[float]:
    iplri = plriv(tspe, mty, alr)
    if snt == Origin.NATURAL:
        y = list(PLSTOT_LUONT[iplri])
    else:
        y = list(PLSTOT_VILJ[iplri])
    # TODO: tämä muutos olisi siistimpi tehdä suoraan taulukkoihin
    y[5] += y[6]
    y[6] = 0
    return y

def plsx_rt(
    alr: SoilCategoryVMI,
    mty: SiteTypeVMI,
    snt: Origin,
    tspe: Species,
    dd: float,
    mood: bool   # TODO: mikä tämän pointti on?
) -> float:
    if snt == Origin.NATURAL or mood:
        ntot = NLUONT[min(alr-1,2)][mty-1][tspe-1]
    else:
        ntot = NVILJ[min(alr-1,2)][mty-1][tspe-1]
    ddyc = -13.5476 + 2.3809*math.log(dd-400) - 0.0028*(dd-400)
    return math.exp(math.log(ntot) + ddyc)

IPOLE = [
    (4,4,4,1,1,1,1,1),
    (4,4,4,1,1,1,1,1),
    (4,4,4,1,1,1,1,1)
]

@dataclasses.dataclass
class Tapula:
    tspe: Species
    yer: float
    plerc: float

def tapula_vilj(vpl: Species) -> Tapula:
    return Tapula(tspe=vpl, yer=1.0, plerc=1.0)

def tapula_luont(
    alr: SoilCategoryVMI,
    mty: SiteTypeVMI,
    dd: float,
    G_seed: float,
    retaos: float,
    kpl: Optional[Species] = None,
    ypl: Optional[Species] = None
) -> Tapula:
    tpl = Species(IPOLE[alr-1][mty-1])
    if tpl == Species.SILVER_BIRCH and dd <= 1000:
        tpl = Species.DOWNY_BIRCH

    ypl = ypl or tpl

    # the original fortran code doesn't init these either, so we'll (kinda) follow it.
    # if this function ever returns a NaN then it's a bug either here or in the original fortran code.
    yer, plerc = float("nan"), float("nan")

    if (
        G_seed <= 0.01
        and not kpl
        and (mty == SiteTypeVMI.VT or (mty == SiteTypeVMI.MT and alr == SoilCategoryVMI.PEAT_PINE))
    ):
        yer, plerc = 0.2, 0.5

    if G_seed > 0.01:
        plerc = 1.0

        if (
            mty <= SiteTypeVMI.MT
            and (
                (ypl >= Species.SILVER_BIRCH and G_seed >= 15.0)
                or (ypl == Species.PINE and G_seed >= 25.0)
            )
        ):
            tpl = Species.SPRUCE
        elif mty >= SiteTypeVMI.CT:
            tpl = Species.PINE
        else:
            tpl = ypl

    if kpl and kpl != tpl:
        if G_seed > 0:
            yer, plerc = 0.5, 0.4
            tpl = kpl
        elif kpl == Species.PINE:
            yer, plerc = 0.2, 0.5
        elif kpl == Species.SPRUCE:
            yer, plerc = 0.1, 0.4
        if kpl != ypl:
            if kpl == Species.PINE:
                if G_seed >= 15 and mty <= SiteTypeVMI.MT:
                    yer, plerc = 0.15, 0.2
                else:
                    yer, plerc = 0.2, 0.3
            elif kpl == Species.SPRUCE:
                if mty >= SiteTypeVMI.VT:
                    yer, plerc = 0.1, 0.2
                if alr == SoilCategoryVMI.PEAT_SPRUCE:
                    yer += 0.2
                    plerc += 0.2
            else:
                if mty == SiteTypeVMI.VT:
                    yer, plerc = 0.3, 0.5
                elif mty >= SiteTypeVMI.CT:
                    yer, plerc = 0.2, 0.3

    if G_seed <= 0.1 and kpl:
        if kpl == Species.PINE:
            retak, retae = 0.7, 0.2
        elif kpl == Species.SPRUCE:
            retak, retae = 0.6, 0.1
        else:
            retak, retae = 0.8, 0.3
        if retaos > 0:
            if tpl > Species.SPRUCE:
                reu = 100
            else:
                reu = 50
            retaos = min(max(100 * (retaos-(reu/100)**2)/retaos, 0), 1)
        # HUOM: tämä sadalla jakaminen on alkuperäisessä fortran-koodissa, onkohan tarkoituksellista?
        # retaos on jo välillä [0,1] joten retaos/100 on aina aika pieni..
        yer = (retaos/100)*retak + (1-(retaos/100))*retae
        tpl = kpl

    return Tapula(
        tspe  = tpl,
        yer   = min(max(yer, 0), 1),
        plerc = min(max(plerc, 0), 1)
    )

@dataclasses.dataclass
class RegenInfo:
    y: List[float]
    ykas: List[float]
    yrt: List[float]
    ykt: List[float]

def synt(
    mty: SiteTypeVMI,
    alr: SoilCategoryVMI,
    snt: Origin,
    dd: float,
    F: float,
    G_seed: float,
    t_muok: float,
    muok: Optional[SoilPrep],
    tspe: Species,
    yer: float,
    plerc: float,
    f_vilj: float,
    surv: float,
    mood: bool   # TODO: ks plsx, tämän voi varmaan tehdä fiksummin
) -> RegenInfo:
    rlo = plsx_rt(alr, mty, snt, tspe, dd, mood) * yer
    if 0.2 <= G_seed < 8.0:
        rst = rlo - 0.5*F
    elif G_seed >= 8.0:
        rst = (1.471-0.05882*G_seed) * (rlo-0.5*F)
    else:
        rst = rlo

    if rst < 0:
        return RegenInfo(y = [0.0]*9, ykas = [0.0]*9, yrt = [0.0]*9, ykt = [0.0]*9)

    y = plsx_y(tspe, mty, alr, snt)
    ycd = (1 - plerc*y[tspe-1]) / (1 - y[tspe-1])
    y[tspe-1] *= plerc
    for i in range(len(y)):
        if i != tspe-1:
            y[i] *= ycd

    rt = rst * mpkmmannut(mty, alr, dd, muok, t_muok)
    if rt <= 200:
        return RegenInfo(y = [0.0]*9, ykas = [0.0]*9, yrt = [0.0]*9, ykt = [0.0]*9)

    rk = casc(rt, snt, G_seed, f_vilj, surv)
    ykas = ykask(tspe, mty, alr, snt)
    ysyn = ysync(tspe, rt, y, rk, ykas)
    rt, y, ykas = ysyn.f, ysyn.y, ysyn.ykas
    yrt = [yy*rt for yy in y]
    ykt = [yk*rk for yk in ykas]
    for i in range(9):
        if yrt[i] < 5:
            yrt[i] = 0
        if ykt[i] < 5:
            ykt[i] = 0

    return RegenInfo(y=y, ykas=ykas, yrt=yrt, ykt=ykt)
