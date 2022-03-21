import math
import statistics
from forestry.ForestDataModels import ForestStand, ReferenceTree
from typing import List, Callable, Iterator

def compounded_growth_factor(growth_percent: float, years: int) -> float:
    try:
        return math.pow(1.0+(growth_percent/100.0), years)
    except:
        return 0.0

def calculate_basal_area(tree: ReferenceTree) -> float:
    """ Single reference tree basal area calculation.

    The tree should contain breast height diameter (in cm) and stesm per hectare for the species spesific calculations.

    :param tree: Single ReferenceTree instance with breast height diameter (in cm) and stems per hectare properties.
    :return reference tree basal area in square meters
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

def calculate_basal_area_weighted_attribute_aggregate(reference_trees: List[ReferenceTree], f: Callable[[ReferenceTree], float]) -> float:
    """ Calcualtes basal area weighted sum for reference trees attribute predefined in function f

    predefined function f contains the logic of calculating reference tree attribute (eg. tree height).
    For example:
        f = lambda x: x.height * calculate_basal_area(x)
    """
    basal_area_total = calculate_attribute_sum(reference_trees, calculate_basal_area)
    attribute_total = calculate_attribute_sum(reference_trees, f)
    return attribute_total / basal_area_total
