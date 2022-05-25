from forestdatamodel.model import ForestStand
try:
    import rpy2.robjects as robjects
except ImportError:
    pass

lmfor_species_map = {
    1: 'pine',
    2: 'spruce',
    3: 'birch',
    4: 'birch',
    5: '',  # aspen, what to do?
    6: '',  # alder, what to do?
    7: 'pine',  # other coniferous, what to do?
    8: 'birch'  # other deciduous, what to do?
}


lmfor_volume_loaded = False


def lmfor_volume(stand: ForestStand) -> float:
    global lmfor_volume_loaded
    if not lmfor_volume_loaded:
        robjects.r.source('./r/lmfor_volume.R')
        lmfor_volume_loaded = True

    source_data = {
        'height': robjects.FloatVector([tree.height for tree in stand.reference_trees]),
        'breast_height_diameter': robjects.FloatVector([tree.breast_height_diameter for tree in stand.reference_trees]),
        'degree_days': robjects.FloatVector([stand.degree_days for _ in range(len(stand.reference_trees))]),
        'species': robjects.StrVector([lmfor_species_map[tree.species] for tree in stand.reference_trees]),
        'measurement_method': robjects.StrVector(['climbed' for _ in range(len(stand.reference_trees))])
    }
    df = robjects.DataFrame(source_data)
    volumes = list(robjects.r['compute_tree_volumes'](df))
    total_volume = round(sum(volumes), 1)
    return total_volume
