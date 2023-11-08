""" Module contains tree generation logic that uses distribution based tree generation models (see. distributions module) """
from typing import Optional
from lukefi.metsi.data.model import ReferenceTree, TreeStratum
from enum import Enum
from lukefi.metsi.forestry.preprocessing import distributions, pre_util
from lukefi.metsi.forestry.preprocessing.naslund import naslund_height, naslund_correction
from lukefi.metsi.forestry.preprocessing.tree_generation_lm import tree_generation_lm


class TreeStrategy(Enum):
    WEIBULL_DISTRIBUTION = 'weibull_distribution'
    LM_TREES = 'LM_TREES'
    HEIGHT_DISTRIBUTION = 'HEIGHT_DISTRIBUTION'
    SKIP = 'skip_tree_generation'


def finalize_trees(reference_trees: list[ReferenceTree], stratum: TreeStratum) -> list[ReferenceTree]:
    """ For all given trees inflates the common variables from stratum. """
    n_trees = len(reference_trees)
    for i, reference_tree in enumerate(reference_trees):
        reference_tree.stand = stratum.stand
        reference_tree.species = stratum.species
        reference_tree.breast_height_age = 0.0 if n_trees == 1 else stratum.get_breast_height_age()
        reference_tree.biological_age = stratum.biological_age
        if reference_tree.breast_height_age == 0.0 and reference_tree.breast_height_diameter > 0.0:
            reference_tree.breast_height_age = 1.0
        reference_tree.tree_number = i + 1
        reference_tree.stems_per_ha = None if reference_tree.stems_per_ha is None \
            else round(reference_tree.stems_per_ha, 2)
        reference_tree.breast_height_diameter = None if reference_tree.breast_height_diameter is None \
            else round(reference_tree.breast_height_diameter, 2)
        reference_tree.height = None if reference_tree.height is None \
            else round(reference_tree.height, 2)
    return reference_trees


def trees_from_weibull(stratum: TreeStratum, **params) -> list[ReferenceTree]:
    """ Generate N trees from weibull distribution.

    For a single tree, stem count and diameter are obtained
    from weibull distribution.
    The height is derived with Näslund height prediction model.
    """
    # stems_per_ha and diameter
    result = distributions.weibull(
        params.get('n_trees'),
        stratum.mean_diameter,
        stratum.basal_area,
        stratum.mean_height)
    # height
    for reference_tree in result:
        height = naslund_height(
            reference_tree.breast_height_diameter,
            stratum.species)
        reference_tree.height = 0.0 if height is None else height
    # height correction
    h_scalar = naslund_correction(stratum.species,
                                  stratum.mean_diameter,
                                  stratum.mean_height)
    for reference_tree in result:
        reference_tree.height = round(h_scalar*reference_tree.height, 2)

    return result


def trees_from_sapling_height_distribution(stratum: TreeStratum, **params) -> list[ReferenceTree]:
    """  Generate N trees from height distribution """
    return distributions.sapling_height_distribution(
        stratum,
        0.0,
        params.get('n_trees'))


def solve_tree_generation_strategy(stratum: TreeStratum, method='weibull') -> str:
    """ Solves the strategy of tree generation for given stratum """

    if stratum.has_height_over_130_cm():
        # big trees
        if stratum.has_diameter() and stratum.has_height() and stratum.has_basal_area() and method == 'weibull':
            return TreeStrategy.WEIBULL_DISTRIBUTION
        elif not stratum.sapling_stratum and stratum.has_diameter() and (stratum.has_basal_area() or stratum.has_stems_per_ha()) and method == 'lm':
            return TreeStrategy.LM_TREES
        elif stratum.has_diameter() and stratum.has_height() and stratum.has_stems_per_ha():
            return TreeStrategy.HEIGHT_DISTRIBUTION
        else:
            return TreeStrategy.SKIP
    else:
        # small trees
        if stratum.has_height() and stratum.sapling_stratum:
            return TreeStrategy.HEIGHT_DISTRIBUTION
        else:
            return TreeStrategy.SKIP


def reference_trees_from_tree_stratum(stratum: TreeStratum, **params) -> list[ReferenceTree]:
    """ Composes N number of reference trees based on values of the stratum.

    The tree generation strategies: weibull distribution, lm_trees and height distribution.
    For big trees generation strategies are weibull or lm_trees depending on configuration, and height distributions.
    Small trees (height < 1.3 meters) are generated with height distribution.

    Big trees need diameter (cm), height (m) and basal area or stem count for the generation process to succeed.
    Small trees need only height (m) and sapling stem count.
    All other cases are skipped.

    :param stratum: Single stratum instance.
    :return: list of reference trees derived from given stratum.
    """
    strategy = solve_tree_generation_strategy(stratum, params.get('method', 'weibull'))
    result = []
    if strategy == TreeStrategy.HEIGHT_DISTRIBUTION:
        result = trees_from_sapling_height_distribution(stratum, **params)
    elif strategy == TreeStrategy.WEIBULL_DISTRIBUTION:
        result = trees_from_weibull(stratum, **params)
    elif strategy == TreeStrategy.LM_TREES:
        result = tree_generation_lm(stratum, stratum.stand.degree_days, stratum.stand.basal_area, **params)
    elif strategy == TreeStrategy.SKIP:
        print(f"\nStratum {stratum.identifier} has no height or diameter usable for generating trees")
        return []
    else:
        raise UserWarning("Unable to generate reference trees from stratum {}".format(stratum.identifier))
    
    result = [ rt for rt in result if round(rt.stems_per_ha,2) > 0.0 ]
    
    return finalize_trees(result, stratum)

