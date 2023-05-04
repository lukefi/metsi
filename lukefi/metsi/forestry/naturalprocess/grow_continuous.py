from pathlib import Path

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from rpy2 import robjects as robjects

from lukefi.metsi.forestry.preprocessing.naslund import naslund_height

species_map: dict[TreeSpecies, int] = {
    TreeSpecies.PINE: 1,
    TreeSpecies.SPRUCE: 2,
    TreeSpecies.SILVER_BIRCH: 3,
    TreeSpecies.DOWNY_BIRCH: 4,
    TreeSpecies.POPLAR: 5,
    TreeSpecies.COMMON_ALDER: 6,
    TreeSpecies.UNKNOWN: 7
}

sitetype_map = {

}

pukkala_loaded = False

def continuous_growth_r(stand: ForestStand, step: int = 5) -> ForestStand:
    """Pukkala growth models implemented by Lauri Mehtätalo"""
    if len(stand.reference_trees) == 0:
        return stand
    global pukkala_loaded
    dir = Path(__file__).parent.parent.resolve() / "r" / "pukkala_growth"
    growth_script_file = dir / "growthfuncs.R"
    if not pukkala_loaded:
        robjects.r.source(str(growth_script_file))
        pukkala_loaded = True

    existing_count = len(stand.reference_trees)
    last_tree_num = stand.reference_trees[-1].tree_number
    tree_data = {
        'id': robjects.IntVector([i for i, _ in enumerate(stand.reference_trees)]),
        'sp': robjects.IntVector([species_map.get(tree.species, 7) for tree in stand.reference_trees]),
        'dbh': robjects.FloatVector([tree.breast_height_diameter for tree in stand.reference_trees]),
        'Ntrees': robjects.FloatVector([tree.stems_per_ha for tree in stand.reference_trees]),
        'sitetype': robjects.IntVector([stand.site_type_category for _ in range(len(stand.reference_trees))]),
        'landclass': robjects.IntVector([stand.soil_peatland_category for _ in range(len(stand.reference_trees))]),
        'TS': robjects.FloatVector([stand.degree_days for _ in range(len(stand.reference_trees))]),
        'y': robjects.IntVector([stand.geo_location[0] for _ in range(len(stand.reference_trees))]),
        'x': robjects.IntVector([stand.geo_location[1] for _ in range(len(stand.reference_trees))]),
        'alt': robjects.FloatVector([stand.geo_location[2] for _ in range(len(stand.reference_trees))]),
        # TODO: harv needs sourcing from cutting history; 0: no operations within last 5 a, 1: yes
        'harv': robjects.IntVector([0 for _ in range(len(stand.reference_trees))]),
        'yr': robjects.IntVector([tree.biological_age for tree in stand.reference_trees])
    }
    df = robjects.DataFrame(tree_data)

    for s in range(step):
        df = robjects.r['grow'](df, path=str(dir) + '/', standArea=stand.area, perLength=1)
        # TODO: R scripts need some refactoring; predheight is not quite usable
        #robjects.r[f'source'](str(dir / "hdmod.R"))
        #df = robjects.r['predheight'](df)
        results = list(df)

        for i in range(len(results[0])):
            if i < existing_count:
                tree = stand.reference_trees[i]
                tree.breast_height_diameter = results[2][i]
                tree.stems_per_ha = results[3][i]
                tree.biological_age = results[11][i]
                #defaulting to Näslund height while predheight is not useable
                tree.height = naslund_height(tree.breast_height_diameter, tree.species)
                tree.breast_height_age = results[11][i] if tree.sapling and tree.height is not None and tree.height >= 1.3 else tree.breast_height_age
                tree.sapling = True if tree.height is None or tree.height < 1.3 else False
            else:
                new_number = last_tree_num + (i+1-existing_count)
                stand.reference_trees.append(ReferenceTree(
                    identifier=f"{stand.identifier}-{new_number}-tree",
                    species={value: key for key, value in species_map.items()}[results[1][i]],
                    breast_height_diameter=results[2][i],
                    stems_per_ha=results[3][i],
                    biological_age=results[11][i],
                    tree_number=new_number,
                    sapling=True
                ))
        existing_count = len(stand.reference_trees)
        last_tree_num = stand.reference_trees[-1].tree_number

    return stand

# R script initialization, library deps
# id missing -> str
# geocoordinate CRS -> YKJ, Lauri tarkistaa CRS:n
# yr value -> biological_age ok, increased
# result ordering guarantee -> yes
# remove trees with stems_per_ha < 0.01
