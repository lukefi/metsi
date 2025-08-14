def tolmax(x: float, lim: float, k: float) -> float:
    if x < lim:
        return k
    else:
        return x

def tolmin(x: float, lim: float, k: float) -> float:
    if x > lim:
        return k
    else:
        return x
