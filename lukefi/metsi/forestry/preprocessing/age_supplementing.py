import typing
from lukefi.metsi.data.model import ReferenceTree, TreeStratum

STRATUM_SUPPLEMENT = 1
INITIAL_TREE_SUPPLEMENT = 2
SAME_TREE_DIAMETER_SUPPLEMENT = 3
SAME_TREE_D13_AGE_SUPPLEMENT = 4


class SupplementStrategy:
    def __init__(self, rt: ReferenceTree):
        self.reference_tree_id: str = rt.identifier
        self.solved: bool = False
        self.strategy: int = None
        self.tree_identifier: str = None


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


def solve_stratum_supplement(reference_tree: ReferenceTree, age_stratums: typing.List[TreeStratum]) -> TreeStratum:
    """ Solves from which stratum the supplementing of reference tree should happen.

    First we initialize a supplement stratum as the first stratum that has the same tree species as reference tree.
    Secondly we try to override the initial supplement stratum by checking if other stratums have a diameter
    such that would represent the reference tree better.

    param: reference_tree: The tree that needs age to be supplemented
    param: age_stratums: List of stratums that contains the best possible
        stratum for used in supplementing

    return: Stratum from which the stratum supplementing will be done
    """
    supplement_stratum = None
    for stratum in age_stratums:
        if supplement_stratum is None:
            if stratum.compare_species(reference_tree):
                supplement_stratum = stratum  # Initial stratum
        else:
            if stratum.has_diameter() and stratum.compare_species(reference_tree):
                supplement_stratum = override_from_diameter(supplement_stratum,
                                                            stratum,
                                                            reference_tree)
    return supplement_stratum


def perform_supplementing(tree_and_strategy: typing.List[typing.Tuple[ReferenceTree, SupplementStrategy]],
                          age_trees: typing.List[ReferenceTree],
                          age_stratums: typing.List[TreeStratum]) -> typing.List[ReferenceTree]:
    for (rt, s) in tree_and_strategy:
        if s.strategy is STRATUM_SUPPLEMENT:
            stratum = solve_stratum_supplement(rt, age_stratums)
            rt.breast_height_age = stratum.breast_height_age
            rt.biological_age = stratum.biological_age
        elif s.strategy is INITIAL_TREE_SUPPLEMENT:
            supplement_tree = next((tree for tree in age_trees if tree.identifier == s.tree_identifier))
            rt.breast_height_age = supplement_tree.breast_height_age
            rt.biological_age = supplement_tree.biological_age
        elif s.strategy is SAME_TREE_DIAMETER_SUPPLEMENT:
            rt.breast_height_age = 2 * rt.breast_height_diameter
            rt.biological_age = 9 + 2 * rt.breast_height_diameter
        elif s.strategy is SAME_TREE_D13_AGE_SUPPLEMENT:
            rt.breast_height_age = 2 * rt.breast_height_diameter
            # Q: bio age calculation is done with 2*diameter as breast_height_age is this correct?
            rt.biological_age = rt.breast_height_age + 9
        else:
            raise UserWarning('error: no supplementing strategy for tree id ' + str(rt))
    reference_trees = [i[0] for i in tree_and_strategy]
    return reference_trees


def final_tree_strategy(reference_tree):
    """ Final strategy for trees that have no age.

    param: reference_tree: Tree with no age
    """
    strategy = SupplementStrategy(reference_tree)
    if not reference_tree.has_biological_age():
        strategy.solved = True
        strategy.strategy = SAME_TREE_DIAMETER_SUPPLEMENT
        return strategy
    if not reference_tree.has_height_over_130_cm():
        strategy.solved = True
        strategy.strategy = SAME_TREE_D13_AGE_SUPPLEMENT
        return strategy
    return strategy


def tree_strategy(reference_tree: ReferenceTree, age_trees: typing.List[ReferenceTree]):
    """ Secondary startegy for trees that have no age

    param: reference_tree: Tree with no age
    param: age_trees: Subset of trees that have age
    """
    strategy = SupplementStrategy(reference_tree)
    for age_tree in age_trees:
        if reference_tree.compare_species(age_tree):
            strategy.solved = True
            strategy.strategy = INITIAL_TREE_SUPPLEMENT
            strategy.tree_identifier = age_tree.identifier
            return strategy
    return strategy


def stratum_strategy(reference_tree: ReferenceTree, stratums: typing.List[TreeStratum]):
    """ Default strategy for trees that do not have age

    param: reference_tree: Tree which does not yet have a age
    param: startums: Subset of stratums that have age
    """
    strategy = SupplementStrategy(reference_tree)
    for stratum in stratums:
        if reference_tree.compare_species(stratum) and stratum.has_diameter():
            strategy.solved = True
            strategy.strategy = STRATUM_SUPPLEMENT
            return strategy
    return strategy


def solve_supplement_strategy(no_age_trees: typing.List[ReferenceTree],
                              age_trees: typing.List[ReferenceTree],
                              age_stratums: typing.List[TreeStratum]) -> typing.List[SupplementStrategy]:
    """ Solveing a supplement strategy happens in a priority order in which stratum strategy
    is with highest priority and using same same tree to supplement the lowest."""
    supplement_strategies = []
    for rt in no_age_trees:
        strategy = stratum_strategy(rt, age_stratums)
        if not strategy.solved:
            strategy = tree_strategy(rt, age_trees)
        if not strategy.solved:
            strategy = final_tree_strategy(rt)
        if strategy.solved:
            supplement_strategies.append((rt, strategy))
        else:
            raise UserWarning('error: supplement strategy for tree number' + str(rt.identifier) + ' can not be solved')
    return supplement_strategies


def supplement_age_for_reference_trees(reference_trees: typing.List[ReferenceTree],
                                       stratums: typing.List[TreeStratum]) -> typing.List[ReferenceTree]:
    """ Supplementing of reference trees that have no d13 age.
    Supplementing happens from subsets of stratums and trees that have d13 age.
    Based on a priority a strategy to supplement is selected and supplementing is performed.
    """
    no_age_trees = list(filter(lambda t: t.breast_height_age is None and t.has_height_over_130_cm(), reference_trees))
    age_trees = list(filter(lambda t: t.breast_height_age or 0 > 0.0, reference_trees))
    age_stratums = list(filter(lambda s: s.breast_height_age > 0.0, stratums))
    trees_and_strategies = solve_supplement_strategy(no_age_trees, age_trees, age_stratums)
    return perform_supplementing(trees_and_strategies, age_trees, age_stratums)
    # TODO: Remove zero stem stratums. See vmi-data-converter issue #55.
