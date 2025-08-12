from typing import Optional
from .coding import SiteTypeVMI, SoilCategoryVMI, Species, TkgTypeVasanderLaine

def turvekangas(
    mty: SiteTypeVMI,
    alr: SoilCategoryVMI,
    spedom: Optional[Species] = None
) -> Optional[TkgTypeVasanderLaine]:
    if mty <= SiteTypeVMI.OMT and alr > SoilCategoryVMI.MINERAL:
        return TkgTypeVasanderLaine.RHTKG1
    if (
        mty == SiteTypeVMI.MT
        and alr > SoilCategoryVMI.MINERAL
        and spedom in (None, Species.PINE, Species.DOWNY_BIRCH)
    ):
        return TkgTypeVasanderLaine.MTKG2
    if (
        mty == SiteTypeVMI.MT
        and alr > SoilCategoryVMI.MINERAL
        and spedom in (Species.SPRUCE, Species.SILVER_BIRCH, Species.ASPEN)
    ):
        return TkgTypeVasanderLaine.MTKG1
    if (
        mty == SiteTypeVMI.VT
        and alr == SoilCategoryVMI.PEAT_PINE
        and spedom in (None, Species.PINE, Species.DOWNY_BIRCH)
    ):
        return TkgTypeVasanderLaine.PTKG2
    if (
        mty == SiteTypeVMI.VT
        and alr > SoilCategoryVMI.MINERAL
        and spedom in (Species.SPRUCE, Species.SILVER_BIRCH)
    ):
        return TkgTypeVasanderLaine.PTKG1
    if mty == SiteTypeVMI.VT and alr == SoilCategoryVMI.PEAT_SPRUCE:
        return TkgTypeVasanderLaine.PTKG1
    if mty == SiteTypeVMI.CT and alr > SoilCategoryVMI.MINERAL:
        return TkgTypeVasanderLaine.VATKG1
    if mty > SiteTypeVMI.CT and alr > SoilCategoryVMI.MINERAL:
        return TkgTypeVasanderLaine.JATK
    return None
