import dataclasses
import math
import numpy as np
from numba import njit
import numpy.typing as npt
from typing import Optional, Sequence
from .coding import LandUseCategoryVMI, Origin, SiteTypeVMI, SoilPrep, Species
from .trans import d2ba

#---- puustotunnukset: log ennusteet ----------------------------------------

#-- mänty --------------------------------------------

@njit
def _ylogG_ma_numba(
    age: float, frel: float, dd: float,
    is_planted: int, is_seeded: int,
    is_omt: int, is_mt: int,
    is_ct: int, is_clt: int,
    is_rocky: int, is_mountain: int,
    is_mal2: int, is_mal3: int,
    kiv: float, sois: float
) -> float:
    return (
        -10.3421
        + 1.975925 * np.log(dd)
        - 39.1114  * 1 / age
        + 2.066733 * is_planted * 1 / np.sqrt(age)
        + 1.863210 * is_seeded  * 1 / np.sqrt(age)
        + 0.386206 * is_omt
        + 0.197305 * is_mt
        - 0.34439  * is_ct
        - 0.15     * is_clt
        - 0.10078  * kiv
        - 0.37456  * sois
        - 0.15     * is_rocky
        - 0.15     * is_mountain
        -          is_mal2 * (dd / 3000.0) ** 1.5
        - 1.5      * is_mal3
        + np.log(frel)
    )
def ylogG_ma(
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    # Enums and boolean logic converted to int flags
    is_planted   = int(snt == Origin.PLANTED)
    is_seeded    = int(snt == Origin.SEEDED)
    is_omt       = int(mal <= 1 and mty <= SiteTypeVMI.OMT)
    is_mt        = int(mal <= 1 and mty == SiteTypeVMI.MT)
    is_ct        = int(mal >= 2 or mty >= SiteTypeVMI.CT)
    is_clt       = int(mal >= 2 or mty >= SiteTypeVMI.ClT)
    is_rocky     = int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
    is_mountain  = int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
    is_mal2      = int(mal >= 2)
    is_mal3      = int(mal >= 3)

    return _ylogG_ma_numba(
        age, frel, dd,
        is_planted, is_seeded,
        is_omt, is_mt,
        is_ct, is_clt,
        is_rocky, is_mountain,
        is_mal2, is_mal3,
        kiv, sois
    )



def ylogN_ma(
    age: float,
    frel: float,
    snt: Origin,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI
) -> float:
    return (
        9.361414
        - 0.58776  * math.log(age)
        - 0.81196  * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        - 0.20146  * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.077442 * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        +            math.log(frel)
    )

def ylogDa_ma(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI
) -> float:
    return (
        -2.01362
        - 9.01319  * age**(-0.5)
        + 0.871257 * math.log(dd)
        + 1.220877 * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        + 0.785906 * int(snt == Origin.SEEDED) * 1/math.sqrt(age)
        + 0.298859 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.111272 * int(mal <= 1 and mty == SiteTypeVMI.MT)
        - 0.18279  * int(mal <= 1 and mty == SiteTypeVMI.CT)
        - 0.23036  * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.04416  * kiv
        - 0.14977  * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogDgM_ma(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -0.89434
        - 7.15591  * age**(-0.5)
        + 0.704244 * math.log(dd)
        + 0.736397 * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        + 0.418311 * int(snt == Origin.SEEDED) * 1/math.sqrt(age)
        + 0.243046 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.089879 * int(mal <= 1 and mty == SiteTypeVMI.MT)
        - 0.14853  * int(mal <= 1 and mty == SiteTypeVMI.CT)
        - 0.16989  * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.02649  * kiv
        - 0.13105  * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogHa_ma(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -5.62134
        - 10.9541  * age**(-0.5)
        + 1.351434 * math.log(dd)
        + 1.089474 * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        + 0.784323 * int(snt == Origin.SEEDED) * 1/math.sqrt(age)
        + 0.296564 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.148140 * int(mal <= 1 and mty == SiteTypeVMI.MT)
        - 0.21179  * int(mal <= 1 and mty == SiteTypeVMI.CT)
        - 0.36327  * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.06823  * kiv
        - 0.20646  * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
    )

def ylogHgM_ma(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -4.27769
        - 9.07592  * age**(-0.5)
        + 1.144920 * math.log(dd)
        + 0.572912 * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        + 0.398371 * int(snt == Origin.SEEDED) * 1/math.sqrt(age)
        + 0.254785 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.122853 * int(mal <= 1 and mty == SiteTypeVMI.MT)
        - 0.17438  * int(mal <= 1 and mty == SiteTypeVMI.CT)
        - 0.29362  * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.04820  * kiv
        - 0.18704  * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
    )

def ylogD100_ma(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI
) -> float:
    return (
        -0.29490
        - 6.26920  * age**(-0.5)
        + 0.632063 * math.log(dd)
        + 0.607386 * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        + 0.373986 * int(snt == Origin.SEEDED) * 1/math.sqrt(age)
        + 0.198765 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.078678 * int(mal <= 1 and mty == SiteTypeVMI.MT)
        - 0.14062  * int(mal <= 1 and mty == SiteTypeVMI.CT)
        - 0.14274  * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.03118  * kiv
        - 0.13060  * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogH100_ma(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -3.54554
        - 8.33716  * age**(-0.5)
        + 1.039037 * math.log(dd)
        + 0.428068 * int(snt == Origin.PLANTED) * 1/math.sqrt(age)
        + 0.300919 * int(snt == Origin.SEEDED) * 1/math.sqrt(age)
        + 0.242263 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        + 0.112042 * int(mal <= 1 and mty == SiteTypeVMI.MT)
        - 0.15247  * int(mal <= 1 and mty == SiteTypeVMI.CT)
        - 0.26735  * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.04337  * kiv
        - 0.17154  * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
    )

#-- kuusi --------------------------------------------

def ylogG_ku(
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    kiv: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        2.934339
        - 97.57   * 1/age
        - 1.000   * math.log(age)
        + 0.82249 * math.log(dd)
        + 0.291   * int(snt == Origin.PLANTED)
        + 0.1826  * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.54499 * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.1445  * kiv
        - 0.35    * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.3     * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.3     * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.3     * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -           int(mal >= 2) * (dd/3000)**(3/2)
        - 1.5     * int(mal >= 3) * 0.5
        + 1.0     * math.log(frel)
    )

def ylogN_ku(
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        17.62006
        - 0.67856  * math.log(age)
        - 0.24824  * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 1.10005  * math.log(dd)
        + 0.157147 * sois
        - 0.14615  * int(snt == Origin.PLANTED)
        + 1.0      * math.log(frel)
    )

def ylogDa_ku(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -0.112
        - 89.1083  * 1/(age+10)
        - 0.48908  * math.log(age)
        + 0.88564  * math.log(dd)
        + 0.235869 * int(mal <= 1 and mty == SiteTypeVMI.OMaT)
        + 0.19524  * int(mal <= 1 and mty == SiteTypeVMI.OMT)
        + 0.2391   * int(snt == Origin.PLANTED)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.2391   * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.0457   * kiv
        - 0.0417   * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogDgM_ku(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -0.81698
        - 75.6435  * 1/(age+10)
        - 0.35186  * math.log(age)
        + 0.919295 * math.log(dd)
        + 0.21157  * int(mal <= 1 and mty == SiteTypeVMI.OMaT)
        + 0.2055   * int(mal <= 1 and mty == SiteTypeVMI.OMT)
        + 0.1007   * int(snt == Origin.PLANTED)
        - 0.03933  * kiv
        - 0.08995  * sois
        - 0.20512  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogHa_ku(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -4.18161
        - 107.598  * 1/(age+10)
        - 0.6237   * math.log(age)
        + 1.515885 * math.log(dd)
        + 0.2326   * int(mal <= 1 and mty == SiteTypeVMI.OMaT)
        + 0.1874   * int(mal <= 1 and mty == SiteTypeVMI.OMT)
        + 0.2294   * int(snt == Origin.PLANTED)
        - 0.09067  * kiv
        - 0.06832  * sois
        - 0.29297  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
    )

def ylogHgM_ku(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -4.7342
        - 87.1555  * 1/(age+10)
        - 0.41086  * math.log(age)
        + 1.467113 * math.log(dd)
        + 0.2024   * int(mal <= 1 and mty == SiteTypeVMI.OMaT)
        + 0.1914   * int(mal <= 1 and mty == SiteTypeVMI.OMT)
        + 0.07673  * int(snt == Origin.PLANTED)
        - 0.0755   * kiv
        - 0.1171   * sois
        - 0.2620   * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
    )

def ylogD100_ku(
    age: float,
    dd: float,
    kiv: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -1.31882
        - 39.7523  * 1/(age+10)
        + 0.746699 * math.log(dd)
        - 0.063    * kiv
        + 0.2124   * int(mal <= 1 and mty == SiteTypeVMI.OMaT)
        + 0.1886   * int(mal <= 1 and mty == SiteTypeVMI.OMT)
        + 0.25934  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogH100_ku(
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -1.84155
        - 0.54546  * math.log(age)
        - 91.1669  * 1/(age+10)
        + 1.167625 * math.log(dd)
        - 0.075    * kiv
        - 0.105    * sois
        + 0.047    * int(snt == Origin.PLANTED)
        + 0.16356  * int(mal <= 1 and mty == SiteTypeVMI.OMaT)
        + 0.1539   * int(mal <= 1 and mty == SiteTypeVMI.OMT)
        - 0.272    * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
    )

#-- koivu --------------------------------------------

def ylogG_ko(
    age: float,
    frel: float,
    dd: float,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -4.91518
        - 37.7247  * 1/age
        - 0.52867  * math.log(age)
        + 1.486638 * math.log(dd)
        + 0.173834 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.47384  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.05     * kiv
        - 0.1      * sois
        - 0.35     * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.3      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.3      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.3      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**(3/2)
        - 1.5      * int(mal >= 3) * 0.5
        + 1.0      * math.log(frel)
    )

def ylogN_ko(
    spe: Species,
    age: float,
    frel: float,
    snt: Origin
) -> float:
    return (
        11.08239
        - 1.09432  * math.log(age)
        - 2.22891  * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
        + 0.401588 * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        + 1.0      * math.log(frel)
    )

def ylogDa_ko(
    spe: Species,
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -1.20010
        - 8.32611  * 1/math.sqrt(age)
        + 0.759056 * math.log(dd)
        + 0.686860 * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
        - 0.1904   * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        - 0.05     * kiv
        - 0.1      * sois
        + 0.108867 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.215638 * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogDgM_ko(
    spe: Species,
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -0.65865
        - 8.65824  * 1/math.sqrt(age)
        + 0.713895 * math.log(dd)
        + 0.657651 * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
        + 0.089617 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.24091  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.19035  * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        - 0.05     * kiv
        - 0.1      * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogHa_ko(
    spe: Species,
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -4.19754
        - 7.79671  * 1/math.sqrt(age)
        + 1.135250 * math.log(dd)
        - 0.19166  * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        + 0.128060 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.23864  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.05     * kiv
        - 0.1      * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
        + 1.0      * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
    )

def ylogHgM_ko(
    spe: Species,
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -3.87941
        - 7.82440  * 1/math.sqrt(age)
        + 1.105648 * math.log(dd)
        - 0.18245  * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        + 0.106894 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.26944  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.05     * kiv
        - 0.1      * sois
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
        + 0.8      * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
    )

def ylogD100_ko(
    spe: Species,
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -1.27043
        - 8.32092  * 1/math.sqrt(age)
        + 0.830717 * math.log(dd)
        - 0.12239  * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        - 0.1      * kiv
        - 0.05     * sois
        + 0.537948 * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
        + 0.043926 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.24502  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.4
    )

def ylogH100_ko(
    spe: Species,
    age: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> float:
    return (
        -4.02488
        - 7.58258  * 1/math.sqrt(age)
        + 1.137578 * math.log(dd)
        - 0.16127  * int(spe == Species.DOWNY_BIRCH or spe >= Species.GRAY_ALDER)
        - 0.1      * kiv
        - 0.05     * sois
        + 0.077555 * int(mal <= 1 and mty <= SiteTypeVMI.OMT)
        - 0.25924  * int(mal >= 2 or mty >= SiteTypeVMI.VT)
        - 0.2      * int(mal >= 2 or mty >= SiteTypeVMI.CT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ClT)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.ROCKY)
        - 0.1      * int(mal >= 2 or mty >= SiteTypeVMI.MOUNTAIN)
        -            int(mal >= 2) * (dd/3000)**3
        -            int(mal >= 3) * 0.5
        + 0.6      * int(snt >= Origin.SEEDED) * 1/math.sqrt(age)
    )

#---- BLUP-mallit ----------------------------------------

def _pt_transf(x: float, i: int) -> float:
    return (x*1.25+2.0) if i in (2,3,6) else x

def _pt_transf_inv(x: float, i: int) -> float:
    return ((x-2.0)/1.25) if i in (2,3,6) else x

def blup_ptunnukset(
    vcov: npt.NDArray,
    y: npt.NDArray,
    p: Sequence[Optional[float]],
) -> npt.NDArray[np.float64]:
    osoite = np.array([i for i,x in enumerate(p) if x])
    if osoite.size == 0:
        return np.maximum(np.array([_pt_transf_inv(y[i]+vcov[i,i]/2, i) for i in range(y.size)]), 0)
    vres = np.log(np.array([_pt_transf(x,i) for i,x in enumerate(p) if x])) - y[osoite]
    vcovi = np.linalg.inv(vcov[np.ix_(osoite, osoite)])
    out = np.zeros(len(p))
    for i,x in enumerate(p):
        if x:
            out[i] = x
        else:
            covx = vcov[i, osoite]
            beta = np.matmul(covx, vcovi)
            yblup = np.matmul(beta, vres)
            vblup = np.matmul(beta, covx.T)
            yi = y[i] + yblup
            vi = vcov[i,i] - vblup
            out[i] = _pt_transf_inv(math.exp(yi + vi/2), i)
    return out

VCOVMA = np.array([
    [.23559,  .08917, .05829, .04454, .07833, .06034, .05753, .05908],
    [.08917,  .21470,-.05543,-.04975,-.03418,-.03002,-.02115,-.01607],
    [.05829, -.05543, .05573, .04258, .05425, .04044, .03424, .03325],
    [.04454, -.04975, .04258, .04559, .03957, .03987, .03553, .03148],
    [.07833, -.03418, .05425, .03957, .06597, .05008, .03462, .04349],
    [.06034, -.03002, .04044, .03987, .05008, .04763, .03362, .04077],
    [.05753, -.02115, .03424, .03553, .03462, .03362, .03537, .03021],
    [.05908, -.01607, .03325, .03148, .04349, .04077, .03021, .03810]
])

def ptma(
    p: Sequence[Optional[float]],
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> npt.NDArray[np.float64]:
    return blup_ptunnukset(
        VCOVMA,
        np.array((
            ylogG_ma(age, frel, dd, snt, kiv, sois, mty, mal),
            ylogN_ma(age, frel, snt, mty, mal),
            ylogDa_ma(age, dd, snt, kiv, sois, mty, mal),
            ylogDgM_ma(age, dd, snt, kiv, sois, mty, mal),
            ylogHa_ma(age, dd, snt, kiv, sois, mty, mal),
            ylogHgM_ma(age, dd, snt, kiv, sois, mty, mal),
            ylogD100_ma(age, dd, snt, kiv, sois, mty, mal),
            ylogH100_ma(age, dd, snt, kiv, sois, mty, mal)
        )),
        p
    )

VCOVKU = np.array([
    [0.188344,0.05826,0.040229,0.031838,0.050299,0.038087,0.046871,0.046835],
    [0.05826,0.17254,-0.04435,-0.043888,-0.03269,-0.031723,-0.032514,-0.01655],
    [0.040229,-0.044351,0.039028,0.030888,0.038453,0.028625,0.030678,0.024548],
    [0.031838,-0.043888,0.030888,0.037886,0.028633,0.034091,0.034116,0.026695],
    [0.050299,-0.03269,0.038453,0.028633,0.045176,0.033273,0.030366,0.029179],
    [0.038087,-0.031723,0.028625,0.034091,0.033273,0.038074,0.035532,0.031195],
    [0.046871,-0.032514,0.030678,0.034116,0.030366,0.035532,0.089253,0.035756],
    [0.046835,-0.016548,0.024548,0.026695,0.029179,0.031195,0.035756,.031977]
])

def ptku(
    p: Sequence[Optional[float]],
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> npt.NDArray[np.float64]:
    return blup_ptunnukset(
        VCOVKU,
        np.array((
            ylogG_ku(age, frel, dd, snt, kiv, mty, mal),
            ylogN_ku(age, frel, dd, snt, sois, mty, mal),
            ylogDa_ku(age, dd, snt, kiv, sois, mty, mal),
            ylogDgM_ku(age, dd, snt, kiv, sois, mty, mal),
            ylogHa_ku(age, dd, snt, kiv, sois, mty, mal),
            ylogHgM_ku(age, dd, snt, kiv, sois, mty, mal),
            ylogD100_ku(age, dd, kiv, mty, mal),
            ylogH100_ku(age, dd, snt, kiv, sois, mty, mal)
        )),
        p
    )

VCOVKO = np.array([
    [.133482,.099069,.010593,.018334,.020546,.026407,.027352,.027318],
    [.09907,.22107,-.058907,-.04009,-.037328,-.02214,-.027272,-.014804],
    [.010593,-.058907,.036626,.027623,.030484,.021816,.023086,.018715],
    [.018334,-.040088,.027623,.027637,.022237,.020464,.023283,.018173],
    [.020546,-.037328,.030484,.022237,.033369,.025361,.019460,.022544],
    [.026407,-.022141,.021816,.020464,.025361,.024467,.019875,.022483],
    [.027352,-.027272,.023086,.023283,.019460,.019875,.027175,.019229],
    [.027318,-.01480,.018715,.018173,.022544,.022483,.019229,.022461]
])

def ptko(
    p: Sequence[Optional[float]],
    spe: Species,
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
) -> npt.NDArray[np.float64]:
    return blup_ptunnukset(
        VCOVKO,
        np.array((
            ylogG_ko(age, frel, dd, kiv, sois, mty, mal),
            ylogN_ko(spe, age, frel, snt),
            ylogDa_ko(spe, age, dd, snt, kiv, sois, mty, mal),
            ylogDgM_ko(spe, age, dd, snt, kiv, sois, mty, mal),
            ylogHa_ko(spe, age, dd, snt, kiv, sois, mty, mal),
            ylogHgM_ko(spe, age, dd, snt, kiv, sois, mty, mal),
            ylogD100_ko(spe, age, dd, snt, kiv, sois, mty, mal),
            ylogH100_ko(spe, age, dd, snt, kiv, sois, mty, mal)
        )),
        p
    )

def g_nissinen_ma(d: float, f: float, age: float) -> float:
    return math.exp(
        -8.918
        + 1.855  * math.log(d)
        + 0.987  * math.log(f)
        + 0.0007 * age
    )

def g_nissinen_ku(d: float, f: float, age: float) -> float:
    return math.exp(
        -8.843
        + 1.851   * math.log(d)
        + 0.981   * math.log(f)
        + 0.00183 * age
    )

def g_nissinen_ko(d: float, f: float) -> float:
    return math.exp(
        -9.084
        + 1.887 * math.log(d)
        + 0.999 * math.log(f)
    )

def dq_ma(d: float, dg: float, snt: Origin, sois: float) -> float:
    return math.exp(
        0.01413
        + 0.64318 * math.log(d)
        + 0.33557 * math.log(dg)
        + 0.00175 * dg
        + 0.0062  * int(snt == Origin.PLANTED)
        - 0.0053  * sois
    )

def dq_ku(d: float, dg: float, snt: Origin, sois: float) -> float:
    return math.exp(
        0.02219
        + 0.6840  * math.log(d)
        + 0.29676 * math.log(dg)
        + 0.00141 * dg
        + 0.0014  * int(snt == Origin.PLANTED)
        - 0.0018  * sois
    )

def dq_muu(d: float, dg: float, snt: Origin, sois: float) -> float:
    return math.exp(
        0.01402
        + 0.72633 * math.log(d)
        + 0.25834 * math.log(dg)
        + 0.00183 * dg
        + 0.005   * int(snt == Origin.PLANTED)
        - 0.005   * sois
    )

def dq_spe(spe: Species, d: float, dg: float, snt: Origin, sois: float) -> float:
    if spe == Species.PINE:
        return dq_ma(d, dg, snt, sois)
    elif spe == Species.SPRUCE:
        return dq_ku(d, dg, snt, sois)
    else:
        return dq_muu(d, dg, snt, sois)

@dataclasses.dataclass
class PtOpt:
    G: Optional[float]     = None
    f: Optional[float]     = None
    Da: Optional[float]    = None
    DgM: Optional[float]   = None
    Ha: Optional[float]    = None
    HgM: Optional[float]   = None
    D100: Optional[float]  = None
    H100: Optional[float]  = None

@dataclasses.dataclass
class Pt:
    G: float
    f: float
    Da: float
    DgM: float
    Ha: float
    HgM: float
    D100: float
    H100: float

def ptalku(
    pt: PtOpt,
    spe: Species,
    age: float,
    frel: float,
    dd: float,
    snt: Origin,
    kiv: float,
    sois: float,
    mty: SiteTypeVMI,
    mal: LandUseCategoryVMI,
    muok: Optional[SoilPrep]
) -> Pt:
    taimi_h = 0
    if snt == Origin.PLANTED:
        if spe in (Species.PINE, Species.SPRUCE):
            taimi_h = 0.15
        elif spe in (
            Species.SILVER_BIRCH,
            Species.DOWNY_BIRCH,
            Species.ASPEN,
            Species.GRAY_ALDER,
            Species.BLACK_ALDER
        ):
            taimi_h = 0.20

    p_in = [pt.G, pt.f, pt.Da, pt.DgM, pt.Ha, pt.HgM, pt.D100, pt.H100]
    npred = 0
    for i,x in enumerate(p_in):
        if x:
            npred += 1
        if npred > 4:
            p_in[i] = None

    gpt = 0
    gnissinen = 0

    if spe in (Species.PINE, Species.CONIFEROUS):
        p = Pt(*ptma(p_in, age, frel, dd, snt, kiv, sois, mty, mal))
        gpt = p.G
        if snt == Origin.PLANTED and (not pt.Ha) and (not pt.G):
            p.Ha += taimi_h
            p.HgM += taimi_h
            p.H100 += taimi_h
        if p.Da > 0 and pt.f:
            gnissinen = g_nissinen_ma(p.Da, pt.f, age)
            if pt.G:
                p.G = pt.G
            else:
                p.G = max(p.G, gnissinen)
    elif spe == Species.SPRUCE:
        if snt == Origin.PLANTED and not (pt.G or pt.Ha or pt.Da or pt.HgM or pt.DgM):
            p = Pt(*ptku(p_in, age, frel, dd, snt, kiv, sois, mty, mal))
            if mty <= SiteTypeVMI.MT and muok == SoilPrep.OTHER:
                muok = SoilPrep.PATCH_MOUNDING
            if muok in (SoilPrep.PATCH_MOUNDING, SoilPrep.DITCH_MOUNDING, SoilPrep.INVERTING):
                h = p.H100 + taimi_h
            elif muok in (SoilPrep.SCALPING, SoilPrep.HARROWING, SoilPrep.OTHER):
                h = p.HgM + taimi_h
            else:
                h = p.Ha + taimi_h
            p_in = [None, pt.f, None, None, h, None, None, None]
        p = Pt(*ptku(p_in, age, frel, dd, snt, kiv, sois, mty, mal))
        if snt == Origin.PLANTED and not (muok or pt.Ha or pt.HgM):
            p.Ha += taimi_h
            p.HgM += taimi_h
            p.H100 += taimi_h
        if p.Ha < 1.3:
            p.Da = 0
        if p.Da > 0 and pt.f:
            # gpt:tä ei aseteta jos tänne ei mennä.
            # onkohan bugi motissa?
            gpt = p.G
            gnissinen = g_nissinen_ku(p.Da, pt.f, age)
            if snt == Origin.PLANTED and (
                (mty == SiteTypeVMI.OMT and muok)
                or (mty <= SiteTypeVMI.OMT and muok and muok >= SoilPrep.PATCH_MOUNDING)
            ):
                gnissinen *= 1.03
                gpt *= 1.03
            if pt.G:
                p.G = pt.G
            else:
                p.G = max(gpt, gnissinen)
    else:
        p = Pt(*ptko(p_in, spe, age, frel, dd, snt, kiv, sois, mty, mal))
        gpt = p.G
        if snt == Origin.PLANTED and not (pt.Ha or pt.HgM):
            p.Ha += taimi_h
            p.HgM += taimi_h
            p.H100 += taimi_h
        if p.Ha < 1.3:
            p.Da = 0
        if p.Da > 0 and pt.f:
            gnissinen = g_nissinen_ko(p.Da, pt.f)
            if pt.G:
                p.G = pt.G
            else:
                p.G = max(p.G, gnissinen)

    if p.H100 < 1.3:
        p.D100 = 0
        p.G = 0
    if p.Ha < 1.3:
        p.Da = 0
    if p.HgM < 1.3:
        p.DgM = 0

    p.Da = max(p.Da, 0)
    p.DgM = max(p.DgM, 0)
    p.D100 = max(p.D100, 0)

    if p.H100 >= 1.3 and p.D100 == 0:
        p.D100 = p.H100/1.3 - 0.8
    if p.Ha >= 1.3 and p.Da == 0:
        p.Da = p.Ha/1.3 - 0.8
    if p.HgM >= 1.3 and p.DgM == 0:
        p.DgM = p.HgM/1.3 - 0.8

    p.Da = max(p.Da, 0.35*p.Ha)
    p.DgM = max(p.DgM, 0.35*p.HgM)
    p.D100 = max(p.D100, 0.35*p.H100)

    if pt.f and pt.G and pt.DgM:
        shape_Ini = pt.G/(math.pi/4*((pt.DgM/100)**2)*pt.f)
        if shape_Ini > 0.99:
            if pt.DgM < 6.0:
                p.G = 0.98 * gpt/shape_Ini
            else:
                p.f = shape_Ini*pt.f / 0.98
    else:
        shape_Ini = 0.5

    if 0 < p.Da < p.DgM:
        dq = dq_spe(spe, p.Da, p.DgM, snt, sois)
        dq_ppa, dq_rulu = 0, 0
        if pt.f:
            dq_ppa = pt.f * d2ba(dq)
            shape_Dq = dq_ppa/(pt.f*d2ba(p.DgM))
            if shape_Dq < 0.99:
                p.G = dq_ppa
        if pt.G:
            dq_rulu = pt.G/d2ba(dq)
            shape_Dq = pt.G/(dq_rulu*d2ba(p.DgM))
            if shape_Dq < 0.99:
                p.f = dq_rulu
        if pt.f and pt.G:
            shape_Ini = pt.G/(math.pi/4*((p.DgM/100)**2)*pt.f)
            if shape_Ini > 0.98 and p.DgM < 6:
                p.G = dq_ppa
            else:
                p.G = pt.G
            if shape_Ini > 0.98 and p.DgM >= 6:
                p.f = dq_rulu
            else:
                p.f = pt.f
    elif p.DgM > 0 and pt.f and gnissinen > 0:
        shape_PT = gpt/(math.pi/4*((p.DgM/100)**2)*pt.f)
        shape_N = gnissinen/(math.pi/4*((p.DgM/100)**2)*pt.f)
        if p.H100 < 8:
            # huom: tässä viitatan shape_Dq, dq_ppa, dq_rulu,
            # mutta ne ei voi olla koskaan laskettuna tässä (ts. ne on nollia).
            # bugi motissa?
            if shape_PT > 0.98 and shape_N > 0.98 and shape_PT < shape_N:
                p.G = 0.98 * gpt/shape_PT
            elif shape_PT > 0.98 and shape_N > 0.98 and shape_N < shape_PT:
                p.G = 0.98 * gnissinen/shape_N
            elif shape_PT <= 0.98 and shape_N > 0.98:
                p.G = gpt
            elif shape_PT > 0.98 and shape_N <= 0.98:
                p.G = gnissinen

    npred = 0
    for i,k in enumerate(["G", "f", "Da", "DgM", "Ha", "HgM", "D100", "H100"]):
        x = getattr(pt, k)
        if x:
            npred += 1
        if npred > 4:
            setattr(p, k, x)

    return p

def ptsurvjs_havu(spe: Species, rdfl: float, dk: float, step: float = 5) -> float:
    expn = math.exp(
        6.86
        - 4.0  * rdfl
        - 40.4 * rdfl/dk
        + 3.0  * int(spe == Species.SPRUCE)
    )
    return (1 + math.exp(-expn))**(-step)

def ptsurvjs_lehti(spe: Species, rdfl: float, dk: float, step: float = 5) -> float:
    expn = math.exp(
        6.27
        - 4.55  * rdfl
        - 33.88 * rdfl/dk
        - 0.25  * int(spe >= Species.ASPEN)
        - 0.5   * int(spe >= Species.CONIFEROUS)
    )
    return (1 + math.exp(-expn))**(-step)

def ptsurvjs(spe: Species, rdfl: float, dk: float, step: float = 5) -> float:
    if spe in (Species.PINE, Species.SPRUCE):
        return ptsurvjs_havu(spe, rdfl, dk, step)
    else:
        return ptsurvjs_lehti(spe, rdfl, dk, step)
