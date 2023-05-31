import math
import statistics
import typing
from enum import Enum
from lukefi.metsi.data.enums.internal import TreeSpecies, DECIDUOUS_SPECIES, CONIFEROUS_SPECIES
from lukefi.metsi.data.model import ReferenceTree, ForestStand, TreeStratum
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


def generate_diameter_threshold(d1: float, d2: float) -> float:
    """ Threshold value for diameter based comparison of two stratums.
    The threshold is generated based on d[0].

    Threshold will have a value based on relative distance of at most 50% of the distance between d[0] and d[1].
    """
    d = sorted((d1, d2), reverse=True)
    return d[0] + (d[1] - d[0]) * (d[0] / (d[1] + d[0]))


def override_from_diameter(initial_stratum: TreeStratum, current_stratum: TreeStratum,
                           reference_tree: ReferenceTree) -> TreeStratum:
    """ Solves if current startum should be used in supplementing of the tree age.
    This happens by calculating a threshold value based on which of the stratum diameters
    is greater and comparing the threshold to reference tree diameter.

    param: initial_stratum: Stratum with the same tree species as reference tree
    param: current_stratum: Stratum i
    param: reference_tree: The tree for which the supplementing will be done

    return: Stratum from which the supplementing will happen
    """
    threshold = generate_diameter_threshold(initial_stratum.mean_diameter,
                                            current_stratum.mean_diameter)
    if threshold > reference_tree.breast_height_diameter:
        return current_stratum
    return initial_stratum


def find_matching_species_stratum_for_tree(reference_tree: ReferenceTree, age_stratums: typing.List[TreeStratum]) -> TreeStratum:
    """ Solves from which stratum the supplementing of reference tree should happen.

    First we initialize a supplement stratum as the first stratum that has the same tree species as reference tree.
    Secondly we try to override the initial supplement stratum by checking if other stratums have a diameter
    such that would represent the reference tree better.

    param: reference_tree: The tree that needs age to be supplemented
    param: age_stratums: List of stratums that contains the best possible
        stratum for used in supplementing

    return: Stratum from which the stratum supplementing will be done
    """
    associated_stratum = None
    for stratum in age_stratums:
        if associated_stratum is None:
            if stratum.compare_species(reference_tree):
                associated_stratum = stratum  # Initial stratum
        else:
            if stratum.has_diameter() and stratum.compare_species(reference_tree):
                associated_stratum = override_from_diameter(associated_stratum,
                                                            stratum,
                                                            reference_tree)
    return associated_stratum


def split_list_by_predicate(items: list, predicate: Callable) -> tuple[list, list]:
    """ Splits a list into two lists based on a predicate.

    :param items: List to be split
    :param predicate: Predicate used to split the list
    :return: Tuple of lists, where the first list contains the items that match the predicate and the second list
        contains the items that do not match the predicate.
    """
    matching_items = []
    non_matching_items = []
    for item in items:
        if predicate(item):
            matching_items.append(item)
        else:
            non_matching_items.append(item)
    return matching_items, non_matching_items


def find_matching_storey_stratum_for_tree(tree: ReferenceTree, strata: list[TreeStratum]) -> Optional[TreeStratum]:
    same_storey_strata = [stratum for stratum in strata if stratum.storey == tree.storey]
    same_species_strata, other_species_strata = split_list_by_predicate(
        same_storey_strata,
        lambda stratum: stratum.species == tree.species)
    if len(same_species_strata) == 1:
        return same_species_strata[0]
    elif len(same_species_strata) > 1:
        return find_matching_species_stratum_for_tree(tree, same_species_strata)
    #TODO: scan other species strata by species precedence list
    #elif len(other_species_strata) > 0:
    #    return find_matching_species_stratum_for_tree(tree, other_species_strata)
    return None

