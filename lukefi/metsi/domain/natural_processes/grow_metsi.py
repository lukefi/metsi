from lukefi.metsi.data.conversion import internal2mela
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.forestry.naturalprocess.metsi_grow.chain import Predict, predict, Species, LandUseCategoryVMI, SiteTypeVMI, \
    SoilCategoryVMI, TaxClass, TaxClassReduction, Origin, Storie
from lukefi.metsi.data.model import ForestStand

from lukefi.metsi.domain.natural_processes.util import update_stand_growth
def __getattr__(name: str):
    if name == "MetsiGrowPredictor":
        from lukefi.metsi.forestry.naturalprocess.grow_metsi import MetsiGrowPredictor
        return MetsiGrowPredictor
    raise AttributeError(name)

def spe2metsi(spe: int) -> Species:
    """Convert RST species code to MetsiGrow compatible Species."""
    code = internal2mela.species_map[TreeSpecies(spe)].value
    # adjust for merged alders
    return Species(code if code <= 6 else code + 1)

def grow_metsi(input_: tuple[ForestStand, None], /, **operation_parameters) -> tuple[ForestStand, None]:
    """
    Wrapper for metsi_grow evolve pipeline. Applies growth step to ForestStand.
    """
    from lukefi.metsi.forestry.naturalprocess.grow_metsi import MetsiGrowPredictor
    step = operation_parameters.get('step', 5)
    stand, _ = input_
    # build predictor
    pred = MetsiGrowPredictor(stand)
    growth = pred.evolve(step=step)
    # apply deltas
    diameters = [t.breast_height_diameter + d for t, d in zip(stand.reference_trees, growth.trees_id)]
    heights    = [t.height + h for t, h in zip(stand.reference_trees, growth.trees_ih)]
    stems = [(t.stems_per_ha or 0.0) + df for t, df in zip(stand.reference_trees, growth.trees_if)]
    update_stand_growth(stand, diameters, heights, stems, step)
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if (t.stems_per_ha or 0.0) >= 1.0]
    return stand, None