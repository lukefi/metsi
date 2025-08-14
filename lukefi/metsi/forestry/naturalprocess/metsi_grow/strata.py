from typing import List, Sequence
from .coding import SaplingType
from .typing import Ints

def group_strata(
    type: Sequence[SaplingType],
    level: Ints
) -> List[int]:
    n = len(level)
    if not n:
        return []
    idx = sorted(range(n), key=lambda i: (level[i], type[i]))
    l = level[idx[0]]
    merge = type[idx[0]] == SaplingType.CULTIVATED
    groups = [0] * n
    g = 0
    for i in idx[1:]:
        if level[i] > l:
            l = level[i]
            if merge:
                merge = False
            else:
                g += 1
        if type[i] == SaplingType.CULTIVATED:
            merge = True
        groups[i] = g
    return groups
