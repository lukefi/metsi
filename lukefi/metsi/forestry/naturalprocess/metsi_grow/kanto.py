from numba import njit
import numpy as np

@njit
def dk(d: float) -> float:
    return 2.0 + 1.25*d

@njit
def dkjs_small(h: float) -> float:
    return np.exp(
        0.4102
        + 1.0360 * np.log(h)
        + (0.037+0.041)**2/2
    )
