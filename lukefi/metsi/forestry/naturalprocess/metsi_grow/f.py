import math

from .coding import Origin

def frel_perk(
    f: float,
    f_level: float,
    f_lower: float,
    h100_perk: float,
    xt_perk: float
) -> float:
    crlvp = f_lower * max(1.0, 2.5/h100_perk) ** (-0.05*xt_perk)
    return f / (f_level + f_lower - crlvp)

def ikaero_comp(
    snt: Origin,
    t_delta: float,
    xt_synt: float
) -> float:
    return (1 + math.exp(-(2*float(snt)*math.sqrt(t_delta+1.3)-xt_synt))) ** (-xt_synt)
