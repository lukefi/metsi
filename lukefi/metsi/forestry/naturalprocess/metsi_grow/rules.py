import dataclasses
from typing import Sequence, Tuple
from .coding import LandUseCategoryVMI, SiteTypeVMI, SoilCategoryVMI, SoilPrep, Species, Storie

def muok_default(mty: SiteTypeVMI, alr: SoilCategoryVMI) -> SoilPrep:
    if mty >= SiteTypeVMI.CT:
        return SoilPrep.NONE
    if mty <= SiteTypeVMI.VT and alr > SoilCategoryVMI.MINERAL:
        return SoilPrep.PATCH_MOUNDING
    if mty == SiteTypeVMI.VT:
        return SoilPrep.HARROWING
    if mty <= SiteTypeVMI.MT:
        return SoilPrep.PATCH_MOUNDING
    return SoilPrep.NONE

def growing_storie(
    storie: Sequence[Storie],
    spe: Sequence[Species],
    spedom: Species,
    small: bool
) -> Tuple[int, Storie]:
    have1 = Storie.UPPER in storie
    have2 = Storie.LOWER in storie
    havemain2 = (Storie.UPPER, spedom) in zip(storie, spe)
    if (have2 or small) and have1:
        return 2, (Storie.UPPER if havemain2 else Storie.LOWER)
    else:
        return 1, Storie.UPPER

def promote_lower_storie(
    f_lower: float,
    f_upper: float,
    h100_lower: float,
    h100_upper: float
) -> bool:
    return f_upper == 0 or h100_upper - h100_lower <= 5 or f_lower <= 250

def ndistrib(f: float) -> int:
    if f > 1400:
        return 10
    if f > 1170:
        return 9
    if f > 960:
        return 8
    if f > 770:
        return 7
    if f > 600:
        return 6
    if f > 400:
        return 5
    if f > 200:
        return 4
    return 3

@dataclasses.dataclass
class Kp:
    mty: SiteTypeVMI
    mal: LandUseCategoryVMI
    alr: SoilCategoryVMI

def kpx(kp: Kp) -> Kp:
    if kp.alr >= SoilCategoryVMI.PEAT_BARREN:
        return Kp(mty=SiteTypeVMI.ROCKY, mal=LandUseCategoryVMI.SCRUB, alr=SoilCategoryVMI.PEAT_PINE)
    if kp.mal == LandUseCategoryVMI.SCRUB:
        return Kp(mty=SiteTypeVMI.ROCKY, mal=kp.mal, alr=kp.alr)
    if kp.mal == LandUseCategoryVMI.WASTE:
        return Kp(mty=SiteTypeVMI.MOUNTAIN, mal=kp.mal, alr=kp.alr)
    return kp
