import math
from numba import njit

@njit
def d2bau(d: float) -> float:
    return math.pi*(d/2)**2

@njit
def d2ba(d: float) -> float:
    return d2bau(d)/10000

@njit
def ba2du(ba: float) -> float:
    return 2*math.sqrt(ba/math.pi)

@njit
def ba2d(ba: float) -> float:
    return ba2du(10000*ba)
