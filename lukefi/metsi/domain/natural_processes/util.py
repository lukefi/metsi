import numpy as np
import numpy.typing as npt
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.data.model import ForestStand


def update_stand_growth(stand: PossiblyLayered[ForestStand],
                        diameters: npt.NDArray[np.float64],
                        heights: npt.NDArray[np.float64],
                        stems: npt.NDArray[np.float64],
                        step: int):
    """In-place update stand's reference trees with given diameters, heights and stem count.
    Increase ages for trees and stand. Remove sapling flag from trees that have grown beyond 1.3m. """
    if stand.reference_trees is None:
        raise MetsiException("Data not vectorized")

    trees = stand.reference_trees

    trees.biological_age = trees.biological_age + step
    trees.breast_height_age = np.where(
        (trees.height < 1.3) & (1.3 <= heights),
        trees.biological_age,
        trees.breast_height_age)
    trees.breast_height_diameter = diameters
    trees.height = heights
    trees.stems_per_ha = stems
    trees.sapling = np.where(
        trees.height >= 1.3,
        False,
        trees.sapling)

    stand.year = (stand.year or 0) + step
