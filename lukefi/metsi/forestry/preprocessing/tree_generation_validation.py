from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from lukefi.metsi.forestry.forestry_utils import calculate_basal_area


def weighted_mean(values: list[float], weights: list[float]) -> float:
    if len(values) == 0 or len(weights) == 0:
        return 0.0

    divisor = sum(weights) if sum(weights) > 0 else len(weights)
    return sum([value * weight for value, weight in zip(values, weights)]) / divisor


def mean(values):
    return 0.0 if len(values) == 0 else sum(values) / len(values)


def round_each_numeric_value_in_list(values: list, decimals: int) -> list:
    return [round(value, decimals) if isinstance(value, (int, float)) else value for value in values]


def create_stratum_tree_comparison_set(
        stratum: TreeStratum, reference_trees: list[ReferenceTree]) -> dict[str, tuple[float, float]]:
    return {'basal_area': (stratum.basal_area,
                           sum([calculate_basal_area(tree) for tree in reference_trees])),
            'stems_per_ha': (stratum.stems_per_ha,
                             sum([tree.stems_per_ha for tree in reference_trees if not tree.sapling])),
            'sapling_stems_per_ha': (stratum.sapling_stems_per_ha,
                                     sum([tree.stems_per_ha for tree in reference_trees if tree.sapling])),
            'mean_diameter': (stratum.mean_diameter,
                              weighted_mean([tree.breast_height_diameter for tree in reference_trees],
                                            [calculate_basal_area(tree) for tree in reference_trees])),
            'mean_height': (stratum.mean_height,
                            weighted_mean([tree.height for tree in reference_trees],
                                          [calculate_basal_area(tree) for tree in reference_trees])),
            'mean_age': (stratum.biological_age,
                         mean([tree.biological_age or 0 for tree in reference_trees]))}


def debug_output_row_from_comparison_set(stratum: TreeStratum, comparison_set: dict[str, tuple[float, float]]) -> list:
    rowdata = [
        stratum.identifier,
        comparison_set['basal_area'][0],
        comparison_set['basal_area'][1],
        comparison_set['stems_per_ha'][0],
        comparison_set['stems_per_ha'][1],
        comparison_set['sapling_stems_per_ha'][0],
        comparison_set['sapling_stems_per_ha'][1],
        comparison_set['mean_diameter'][0],
        comparison_set['mean_diameter'][1],
        comparison_set['mean_height'][0],
        comparison_set['mean_height'][1],
        comparison_set['mean_age'][0],
        comparison_set['mean_age'][1]
    ]

    return round_each_numeric_value_in_list(rowdata, 2)


def debug_output_header_row() -> list:
    return [
        'stratum_id',
        'strat_G',
        'trees_G',
        'strat_stems',
        'trees_stems',
        'strat_sap_stems',
        'trees_sap_stems',
        'strat_d',
        'trees_d',
        'strat_h',
        'trees_h',
        'strat_a',
        'trees_a'
    ]
