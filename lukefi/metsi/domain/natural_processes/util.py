import numpy as np
import numpy.typing as npt
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.data.model import ForestStand


def update_stand_growth(
        stand: ForestStand,
        diameters: list[float],
        heights: list[float],
        stems: list[float],
        step: int):
    """In-place update stand's reference trees with given diameters, heights and stem count.
    Increase ages for trees and stand. Remove sapling flag from trees that have grown beyond 1.3m. """
    for i, t in enumerate(stand.reference_trees):
        height_before_growth = t.height
        t.breast_height_diameter = diameters[i]
        t.height = heights[i]
        t.stems_per_ha = stems[i]
        t.biological_age += step
        if height_before_growth < 1.3 <= t.height:
            t.breast_height_age = t.biological_age
        if t.height >= 1.3 and t.sapling:
            t.sapling = False
    stand.year += step


def update_stand_growth_vectorized(stand: ForestStand,
                                   diameters: npt.NDArray[np.float64],
                                   heights: npt.NDArray[np.float64],
                                   stems: npt.NDArray[np.float64],
                                   step: int):
    """In-place update stand's reference trees with given diameters, heights and stem count.
    Increase ages for trees and stand. Remove sapling flag from trees that have grown beyond 1.3m. """
    if stand.reference_trees_soa is None:
        raise MetsiException("Data not vectorized")

    trees = stand.reference_trees_soa

    height_before_growth = trees.height.copy()
    trees.breast_height_diameter = diameters
    trees.height = heights
    trees.stems_per_ha = stems
    trees.biological_age += step
    trees.breast_height_age = np.where(
        (height_before_growth < 1.3) & (1.3 <= trees.height),
        trees.biological_age,
        trees.breast_height_age)
    trees.sapling = np.where(
        trees.height >= 1.3,
        False,
        trees.sapling)
    if stand.year is not None:
        stand.year += step
    else:
        stand.year = step
