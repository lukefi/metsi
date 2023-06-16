from pathlib import Path

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import TreeStratum, ReferenceTree
from rpy2 import robjects as robjects

lm_tree_generation_loaded = False


def determine_hmalli_value(species: TreeSpecies):
    if species in (TreeSpecies.PINE, TreeSpecies.OTHER_PINE, TreeSpecies.SHORE_PINE):
        return 1
    elif species.is_coniferous():
        return 2
    else:
        return 3


def tree_generation_lm(stratum: TreeStratum, degree_days: float, stand_basal_area: float, n=10, mode="dcons") -> list[ReferenceTree]:
    global lm_tree_generation_loaded
    dir = Path(__file__).parent.parent.resolve() / "r"
    growth_script_file = dir / "lm_tree_generation.R"
    if not lm_tree_generation_loaded:
        robjects.r.source(str(growth_script_file))
        lm_tree_generation_loaded = True

    stratum_data = {
        'DGM': robjects.FloatVector([stratum.mean_diameter]),
        'HGM': robjects.FloatVector([stratum.mean_height]),
        'G': robjects.FloatVector([stand_basal_area]),
        'Gos': robjects.FloatVector([stratum.basal_area]),
        'spe': robjects.FloatVector([stratum.species.value]),
        'DDY': robjects.FloatVector([degree_days])
    }

    source_trees = stratum.__dict__.get('_trees', [])

    tree_data = {
        'lpm': robjects.FloatVector([tree.breast_height_diameter or robjects.NA_Real for tree in source_trees]),
        'height': robjects.FloatVector([tree.height or robjects.NA_Real for tree in source_trees])
    }
    df = robjects.DataFrame(stratum_data)
    df2 = robjects.DataFrame(tree_data)
    result_df = robjects.r['generoi.kuvauspuut'](df, df2, path=str(dir) + '/', tapa=mode, n=n, hmalli=determine_hmalli_value(stratum.species))

    trees = []
    for i in range(len(result_df)):
        trees.append(ReferenceTree(
            breast_height_diameter=result_df.rx2(8)[i],
            stems_per_ha=result_df.rx2(9)[i],
            height=result_df.rx2(10)[i],
            species=stratum.species,
            biological_age=stratum.biological_age,
            sapling=result_df.rx2(10)[i] < 1.3
        ))

    return trees
