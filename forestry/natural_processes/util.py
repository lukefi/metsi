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