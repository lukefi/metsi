from collections.abc import Callable
from lukefi.metsi.data.model import ForestStand

def iterative_thinning(
        stand: ForestStand,
        thinning_factor: float,
        thin_predicate: Callable,
        extra_factor_solver: Callable
) -> ForestStand:
    """ Iteratively decreases the stem count of stand reference trees until stoppin condition is met.

    The parameter :extra_factor_solver: may be used to customize the removal of stems.
    If given as (lambda i,n,c: 0) removes same amount of stems from each tree (a.k.a even thinning).

    :param stand: Forest stand instance of forestdatamodel library
    :param thinning_factor: Intensity of the thinning on each iteration
    :param thin_predicate: Condition to stop thinning
    :param extra_factor_solver: Gradually increasing proportion of removal
    """
    n = len(stand.reference_trees)
    c = thinning_factor

    while thin_predicate(stand):
        # cut until lower bound reached
        for i, rt in enumerate(stand.reference_trees):
            thin_factor = c + extra_factor_solver(i, n, c)
            thin_factor = 1.0 if thin_factor > 1.0 else thin_factor
            rt.stems_per_ha *= thin_factor

    return stand
