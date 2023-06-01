import math
import statistics
from enum import Enum
from lukefi.metsi.data.enums.internal import TreeSpecies, DECIDUOUS_SPECIES, CONIFEROUS_SPECIES
from lukefi.metsi.data.model import ReferenceTree, ForestStand, TreeStratum
from typing import Optional
from collections.abc import Callable


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


def solve_dominant_height(reference_trees: list[ReferenceTree]) -> float:
    heights = list(map(lambda tree: tree.height, reference_trees))
    dominant_height = statistics.median(heights)
    return dominant_height


def calculate_attribute_sum(reference_trees: list[ReferenceTree], f: Callable) -> float:
    return sum(map(f, reference_trees))


def calculate_basal_area_weighted_attribute_sum(reference_trees: list[ReferenceTree],
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

    Threshold will have a value based on relative distance of at most 50% of the distance between d[0] and d[1].
    """
    greater = max((d1, d2))
    lesser = min((d1, d2))
    return greater + (lesser - greater) * (greater / (lesser + greater))


def override_from_diameter(initial_stratum: TreeStratum, candidate_stratum: TreeStratum,
                           reference_tree: ReferenceTree) -> TreeStratum:
    """ Out of given strata, return the stratum for which the mean diameter better matches the reference tree diameter.
    This happens by calculating a threshold value based on which of the stratum diameters
    is greater and comparing the threshold to reference tree diameter.

    :param initial_stratum: Stratum which is assumed as the current match for the reference tree
    :param candidate_stratum: Stratum which is tested for better compatiblity than the initial stratum
    :param reference_tree: The tree for which the supplementing will be done

    :returns: the better matching stratum
    """
    threshold = generate_diameter_threshold(initial_stratum.mean_diameter, candidate_stratum.mean_diameter)
    if threshold > reference_tree.breast_height_diameter:
        return candidate_stratum
    return initial_stratum


def find_matching_stratum_by_diameter(reference_tree: ReferenceTree, strata: list[TreeStratum]) -> Optional[TreeStratum]:
    """ Solves from which stratum the supplementing of reference tree should happen.

    Return a stratum that has the closest diameter to the reference tree diameter.

    :param reference_tree: A reference tree for which a matching stratum needs to be found
    :param strata: list of stratums from which a diameter match is searched
    :returns: a matching stratum or None if not match is possible
    """
    if len(strata) == 0:
        return None
    associated_stratum = strata[0]
    for stratum in strata[1:]:
        if stratum.has_diameter():
            # TODO: this method is definitely not stable with strata lists of different orderings
            # i.e. it will return different result depending on which order the strata are given
            # this is not safe to use in other contexts than the current one being refactored
            # and requires a more robust solution
            associated_stratum = override_from_diameter(associated_stratum, stratum, reference_tree)
    return associated_stratum


def split_list_by_predicate(items: list, predicate: Callable) -> tuple[list, list]:
    """ Splits a list into two lists based on a predicate.

    :param items: list to be split
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


def find_strata_by_similar_species(species: TreeSpecies, strata: list[TreeStratum]) -> list[TreeStratum]:
    """
    Find a list of strata which have a similar species to the given species. Out of deciduous trees,
    silver birch is considered most similar to downy birch and vice versa.
    :param species:
    :param strata:
    :return:
    """
    candidates = []

    if species.is_deciduous():
        if species == TreeSpecies.DOWNY_BIRCH:
            candidates.extend(filter(lambda s: s.species == TreeSpecies.SILVER_BIRCH, strata))
        elif species == TreeSpecies.SILVER_BIRCH:
            candidates.extend(filter(lambda s: s.species == TreeSpecies.DOWNY_BIRCH, strata))
        else:
            candidates.extend(filter(lambda s: s.species.is_deciduous(), strata))
    elif species.is_coniferous():
        candidates.extend(filter(lambda s: s.species.is_coniferous(), strata))

    return candidates


def find_matching_storey_stratum_for_tree(tree: ReferenceTree, strata: list[TreeStratum]) -> Optional[TreeStratum]:
    same_storey_strata = [stratum for stratum in strata if stratum.storey == tree.storey]
    same_species_strata, other_species_strata = split_list_by_predicate(
        same_storey_strata,
        lambda stratum: stratum.species == tree.species)
    candidate_strata = []
    if len(same_species_strata) > 0:
        candidate_strata = same_species_strata
    elif len(other_species_strata) > 0:
        candidate_strata = find_strata_by_similar_species(tree.species, other_species_strata)
    # TODO: species selection by diameter is not stable for this purpose
    #selected_stratum = find_matching_stratum_by_diameter(tree, candidate_strata)
    selected_stratum = candidate_strata[0] if len(candidate_strata) > 0 else None
    return selected_stratum
