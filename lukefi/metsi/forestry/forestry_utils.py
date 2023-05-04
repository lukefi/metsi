import math
import statistics
from enum import Enum
from lukefi.metsi.data.model import ReferenceTree, ForestStand
from typing import List, Callable, Optional


def compounded_growth_factor(growth_percent: float, years: int) -> float:
    try:
        return math.pow(1.0 + (growth_percent / 100.0), years)
    except:
        return 0.0


def solve_dominant_height_c_largest(stand, c: int = 100):
    """ Calculate stands weighted average of c largest stems (100 by default) """
    sorted_trees = sorted(stand.reference_trees, key=lambda rt: rt.breast_height_diameter, reverse=True)
    dw_sum, n = 0, 0
    for rt in sorted_trees:
        d = rt.breast_height_diameter
        w = rt.stems_per_ha
        if n + w >= c:
            wn = (c - n) # notice only portion of stems as last weight
            dw_sum += d * wn
            n = c
            break
        # weighted sum
        dw_sum += d * w
        n += w
    # average of weighted sums
    return dw_sum / n if n > 0 else 0


def overall_basal_area(trees: list[ReferenceTree]) -> float:
    """ Overall basal area of trees in square meters (m^2) """
    return sum(calculate_basal_area(rt) for rt in trees)


def overall_stems_per_ha(trees: list[ReferenceTree]) -> float:
    """ Sums up the stems of all reference trees """
    return sum(rt.stems_per_ha for rt in trees)


def solve_dominant_species(trees: list[ReferenceTree]) -> Optional[Enum]:
    """ Solves dominant species of trees based on basal area """
    if len(trees) == 0:
        return None
    spe_ba = [(rt.species, calculate_basal_area(rt)) for rt in trees]
    bucket = {x[0]: 0.0 for x in spe_ba}
    for spe, basal_area in spe_ba:
        bucket[spe] += basal_area
    return max(bucket, key=bucket.get)


def calculate_basal_area(tree: ReferenceTree) -> float:
    """ Single reference tree basal area calculation.

    The tree should contain breast height diameter (in cm) and stesm per hectare for the species spesific calculations.

    :param tree: Single ReferenceTree instance with breast height diameter (in cm) and stems per hectare properties.
    :return reference tree basal area in square meters (m^2)
    """
    meters_factor = 0.01
    radius = tree.breast_height_diameter * 0.5 * meters_factor
    single_basal_area = math.pi * math.pow(radius, 2)
    return single_basal_area * tree.stems_per_ha


def solve_dominant_height(reference_trees: List[ReferenceTree]) -> float:
    heights = list(map(lambda tree: tree.height, reference_trees))
    dominant_height = statistics.median(heights)
    return dominant_height


def calculate_attribute_sum(reference_trees: List[ReferenceTree], f: Callable) -> float:
    return sum(map(f, reference_trees))


def calculate_basal_area_weighted_attribute_sum(reference_trees: List[ReferenceTree],
                                                      f: Callable[[ReferenceTree], float]) -> float:
    """ Calcualtes basal area weighted sum for reference trees attribute predefined in function f

    predefined function f contains the logic of calculating reference tree attribute (eg. tree height).
    For example:
        f = lambda x: x.height * calculate_basal_area(x)
    """
    basal_area_total = calculate_attribute_sum(reference_trees, calculate_basal_area)
    attribute_total = calculate_attribute_sum(reference_trees, f)
    return attribute_total / basal_area_total

def mean_age_stand(stand: ForestStand) -> float:
    stems = overall_stems_per_ha(stand.reference_trees)
    if stems > 0:
        agesum = sum(rt.stems_per_ha * rt.biological_age for rt in stand.reference_trees)
        mean_age = agesum/stems
    else:
        mean_age = 0
    return mean_age

