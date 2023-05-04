""" Module contains tree generation logic that uses distribution based tree generation models (see. distributions module) """
from typing import Optional, List
from lukefi.metsi.data.model import ReferenceTree, TreeStratum
from enum import Enum
from lukefi.metsi.forestry.preprocessing import distributions
from lukefi.metsi.forestry.preprocessing.naslund import naslund_height

class TreeStrategy(Enum):
    WEIBULL_DISTRIBUTION = 'weibull_distribution'
    HEIGHT_DISTRIBUTION = 'HEIGHT_DISTRIBUTION'
    SKIP = 'skip_tree_generation'


def finalize_trees(reference_trees: List[ReferenceTree], stratum: TreeStratum) -> List[ReferenceTree]:
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


def trees_from_weibull(stratum: TreeStratum, n_trees: int) -> List[ReferenceTree]:
    """ Generate N trees from weibull distribution.

    For a single tree, stem count and diameter are obtained
    from weibull distribution.
    The height is derived with Näslund height prediction model.
    """
    # stems_per_ha and diameter
    result = distributions.weibull(
        n_trees,
        stratum.mean_diameter,
        stratum.basal_area,
        stratum.mean_height)
    # height
    for reference_tree in result:
        height = naslund_height(
            reference_tree.breast_height_diameter,
            stratum.species)
        reference_tree.height = 0.0 if height is None else height
    return result


def trees_from_sapling_height_distribution(stratum: TreeStratum, n_trees: Optional[int] = None) -> List[ReferenceTree]:
    """  Generate N trees from height distribution """
    return distributions.sapling_height_distribution(
        stratum,
        0.0,
        n_trees)


def solve_tree_generation_strategy(stratum: TreeStratum) -> str:
    """ Solves the strategy of tree generation for given stratum """
    if stratum.has_height_over_130_cm():
        # big trees
        if stratum.has_diameter() and stratum.has_height() and stratum.has_basal_area():
            return TreeStrategy.WEIBULL_DISTRIBUTION
        elif stratum.has_diameter() and stratum.has_height() and stratum.has_stems_per_ha():
            return TreeStrategy.HEIGHT_DISTRIBUTION
        else:
            return TreeStrategy.SKIP
    else:
        # small trees
        if stratum.has_height() and stratum.has_sapling_stems_per_ha():
            return TreeStrategy.HEIGHT_DISTRIBUTION
        else:
            return TreeStrategy.SKIP


def reference_trees_from_tree_stratum(stratum: TreeStratum, n_trees: Optional[int] = 10) -> List[ReferenceTree]:
    """ Composes N number of reference trees based on values of the stratum.

    The tree generation strategies: weibull distribution and height distribution.
    For big trees generation strategies are weibull and height distributions.
    Small trees (height < 1.3 meters) are generated with height distribution.

    Big trees need diameter (cm), height (m) and basal area or stem count for the generation process to succeed.
    Small trees need only height (m) and sapling stem count.
    All other cases are skipped.

    :param stratum: Single stratum instance.
    :param (optional) n_trees: Number of reference trees to be generated (10 by default).
    :return: List of reference trees derived from given stratum.
    """
    strategy = solve_tree_generation_strategy(stratum)
    result = []
    if strategy == TreeStrategy.HEIGHT_DISTRIBUTION:
        result = trees_from_sapling_height_distribution(stratum, n_trees)
    elif strategy == TreeStrategy.WEIBULL_DISTRIBUTION:
        result = trees_from_weibull(stratum, n_trees)
    elif strategy == TreeStrategy.SKIP:
        return []
    else:
        raise UserWarning("Unable to generate reference trees from stratum {}".format(stratum.identifier))
    return finalize_trees(result, stratum)

