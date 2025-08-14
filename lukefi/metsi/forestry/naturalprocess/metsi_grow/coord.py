from typing import Tuple

def etrs_tm35_to_ykj(Y: float, X: float) -> Tuple[float, float]:
    A = 1.0004021568
    B = 0.0000031984
    C = 119.9646 / 1000
    D = 2999947.3597 / 1000
    return (
        A * Y - B * X + C,
        B * Y + A * X + D
    )
