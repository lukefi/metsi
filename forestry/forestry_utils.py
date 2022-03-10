import math
import statistics
from forestry.ForestDataModels import ForestStand, ReferenceTree
from typing import List, Callable

def calculate_basal_area(tree: ReferenceTree) -> float:
    return math.pi * math.pow(tree.breast_height_diameter / 200, 2) * tree.stems_per_ha

def solve_dominant_height(reference_trees: List[ReferenceTree]) -> float:
    heights = list(map(lambda tree: tree.height, reference_trees))
    dominant_height = statistics.median(heights)
    return dominant_height

def filter_reference_trees_by_species(reference_trees: List[ReferenceTree]) -> List[ReferenceTree]:
    species = set(map(lambda tree: tree.species, reference_trees))
    trees_by_species = []
    for spe in species:
        trees = list(filter(lambda tree: tree.species == spe, reference_trees))
        trees_by_species.append(trees)
    return trees_by_species

def calculate_attribute_sum(reference_trees: List[ReferenceTree], f: Callable) -> float:
    total = 0
    for tree in reference_trees:
        total = total + f(tree)
    return total

def calculate_attribute_aggregate(reference_trees: List[ReferenceTree], f: Callable) -> float:
    basal_area_total = calculate_attribute_sum(reference_trees, calculate_basal_area)
    attribute_total = calculate_attribute_sum(reference_trees, f)
    return attribute_total / basal_area_total
