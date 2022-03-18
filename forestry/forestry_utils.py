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
    """ Single tree basal area calculation.

    :param tree: Single ReferenceTree instance that must contain members of breast height diameter (in meters) and stems per hectare.
    """
    radius_m = 200
    try:
        return math.pi * math.pow(tree.breast_height_diameter / radius_m, 2) * tree.stems_per_ha
    except:
        return 0.0

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
