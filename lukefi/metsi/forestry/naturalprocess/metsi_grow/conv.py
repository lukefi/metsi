from typing import Optional
from .coding import PeatTypeSINKA, Species

vmi_sinka = {
    1: 3, 2: 9, 3: 15, 4: 14, 5: 19, 6: 20, 8: 22, 9: 23, 12: 1, 13: 2, 14: 8, 15: 13, 16: 4,
    17: 10, 18: 16, 19: 25, 20: 27, 23: 6, 25: 11, 16: 12
}

def vmi2sinka(vmi: int) -> Optional[PeatTypeSINKA]:
    c = vmi_sinka.get(vmi)
    return PeatTypeSINKA(c) if c else None

def spe4(spe: Species) -> int:
    if spe == 8:
        return 1
    if spe == 5:
        return 3
    return min(spe, 4)
