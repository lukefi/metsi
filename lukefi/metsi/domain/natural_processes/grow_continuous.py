from functools import cache
from typing import Callable

from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.data.model import ForestStand, ReferenceTree
from lukefi.metsi.forestry.preprocessing.naslund import naslund_height
from rpy2 import robjects as robjects

from lukefi.metsi.sim.core_types import OpTuple

species_map: dict[TreeSpecies, int] = {
    TreeSpecies.PINE: 1,
    TreeSpecies.SPRUCE: 2,
    TreeSpecies.SILVER_BIRCH: 3,
    TreeSpecies.DOWNY_BIRCH: 4,
    TreeSpecies.POPLAR: 5,
    TreeSpecies.COMMON_ALDER: 6,
    TreeSpecies.UNKNOWN: 7
}


@cache
def grow_continuous_r(script_path: str, scripts: tuple[str]) -> tuple[Callable, ...]:
    """Return a cached growth function to call with parameters"""
    for script_name in scripts:
        robjects.r.source(f"{script_path}/{script_name}")

    def growth_fn(dataframe: robjects.DataFrame, step: int, area: float) -> robjects.DataFrame:
        return robjects.r['grow'](dataframe, path=f"{script_path}/", standArea=area, perLength=step)

    def height_fn(dataframe: robjects.DataFrame):
        return robjects.r['predheight'](dataframe)

    return growth_fn, height_fn


def stand_to_dataframe(stand: ForestStand) -> robjects.DataFrame:
    """Convert stand and trees to dataframe exepected by growthfuncs.R function grow"""
    tree_data = {
        'id': robjects.IntVector([i for i, _ in enumerate(stand.reference_trees)]),
        'sp': robjects.IntVector([species_map.get(tree.species, 7) for tree in stand.reference_trees]),
        'dbh': robjects.FloatVector([tree.breast_height_diameter for tree in stand.reference_trees]),
        'Ntrees': robjects.FloatVector([tree.stems_per_ha for tree in stand.reference_trees]),
        'sitetype': robjects.IntVector([stand.site_type_category.value for _ in range(len(stand.reference_trees))]),
        'landclass': robjects.IntVector([stand.soil_peatland_category.value for _ in range(len(stand.reference_trees))]),
        # TODO: degree_days is not readily available in source data
        'TS': robjects.FloatVector([stand.degree_days or 1234.0 for _ in range(len(stand.reference_trees))]),
        'y': robjects.IntVector([stand.geo_location[0] for _ in range(len(stand.reference_trees))]),
        'x': robjects.IntVector([stand.geo_location[1] for _ in range(len(stand.reference_trees))]),
        # TODO: height above sea level is not readily available in source data
        'alt': robjects.FloatVector([stand.geo_location[2] or 0.0 for _ in range(len(stand.reference_trees))]),
        # TODO: harv needs sourcing from cutting history; 0: no operations within last 5 a, 1: yes
        'harv': robjects.IntVector([0 for _ in range(len(stand.reference_trees))]),
        'yr': robjects.IntVector([tree.biological_age for tree in stand.reference_trees])
    }

    return robjects.DataFrame(tree_data)


def grow_continuous(input: OpTuple[ForestStand], **operation_parameters) -> ForestStand:
    stand, collected_data = input
    step = operation_parameters.get('step', 5)

    # TODO: predheight function requires dh.param from hdmod.R. hdmod.R is not usable as a side-effectful script.
    #growth_fn, height_fn = grow_continuous_r('r/pukkala_growth', ('growthfuncs.R', 'hdmod.R'))
    growth_fn, height_fn = grow_continuous_r('r/pukkala_growth', ('growthfuncs.R',))
    results = growth_fn(stand_to_dataframe(stand), step, stand.area)
    #results = height_fn(results)
    list_results = list(results)
    last_tree_nr = max([tree.tree_number for tree in stand.reference_trees])

    for i in range(len(list_results[0])):
        existing_count = len(stand.reference_trees)
        species = {value: key for key, value in species_map.items()}[results[1][i]]
        if i < existing_count:
            tree = stand.reference_trees[i]
            tree.breast_height_diameter = results[2][i]
            tree.stems_per_ha = results[3][i]
            tree.biological_age = results[11][i]
            tree.height = naslund_height(results[2][i], species)  # TODO: get predheight working
        else:
            last_tree_nr += 1
            stand.reference_trees.append(ReferenceTree(
                identifier=stand.identifier + f"-tree-{last_tree_nr}",
                species=species,
                breast_height_diameter=results[2][i],
                stems_per_ha=results[3][i],
                height=naslund_height(results[2][i], species) or 0.0,  # TODO: get predheight working
                biological_age=results[11][i],
                tree_number=last_tree_nr
            ))

    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha * stand.area >= 1.0]
    stand.year += step

    return stand, collected_data

# geocoordinate CRS -> YKJ, Lauri tarkistaa CRS:n

