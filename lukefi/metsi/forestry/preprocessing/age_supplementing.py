from lukefi.metsi.data.model import ReferenceTree, TreeStratum
from lukefi.metsi.forestry.forestry_utils import find_matching_stratum_by_diameter

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


def perform_supplementing(tree_and_strategy: list[tuple[ReferenceTree, SupplementStrategy]],
                          age_trees: list[ReferenceTree],
                          age_stratums: list[TreeStratum]) -> list[ReferenceTree]:
    for (rt, s) in tree_and_strategy:
        if s.strategy is STRATUM_SUPPLEMENT:
            same_species_strata = [
                stratum for stratum in age_stratums if stratum.species == rt.species and stratum.has_diameter()
            ]
            stratum = find_matching_stratum_by_diameter(rt, same_species_strata)
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


def tree_strategy(reference_tree: ReferenceTree, age_trees: list[ReferenceTree]):
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


def stratum_strategy(reference_tree: ReferenceTree, stratums: list[TreeStratum]):
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


def solve_supplement_strategy(no_age_trees: list[ReferenceTree],
                              age_trees: list[ReferenceTree],
                              age_stratums: list[TreeStratum]) -> list[SupplementStrategy]:
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


def supplement_age_for_reference_trees(reference_trees: list[ReferenceTree],
                                       stratums: list[TreeStratum]) -> list[ReferenceTree]:
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
