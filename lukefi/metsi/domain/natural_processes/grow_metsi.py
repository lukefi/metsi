# Licensed under the Mozilla Public License 2.0 (MPL-2.0).
#
# NOTE:
# This file imports code from MetsiGrow.
# MetsiGrow is NOT licensed under MPL-2.0.
# MetsiGrow is released under a separate Source Available – Non-Commercial license.
# See MetsiGrow's LICENSE-NC.md for full details.


from lukefi.metsi.data.conversion import internal2mela
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.forestry.naturalprocess.MetsiGrow.metsi_grow.chain import Predict, predict, Species, LandUseCategoryVMI, SiteTypeVMI, \
    SoilCategoryVMI, TaxClass, TaxClassReduction, Origin, Storie
from lukefi.metsi.data.model import ForestStand

from lukefi.metsi.domain.natural_processes.util import update_stand_growth
from lukefi.metsi.sim.collected_data import OpTuple
def __getattr__(name: str):
    if name == "MetsiGrowPredictor":
        from lukefi.metsi.forestry.naturalprocess.MetsiGrow.grow_metsi import MetsiGrowPredictor
        return MetsiGrowPredictor
    raise AttributeError(name)

def spe2metsi(spe: int) -> Species:
    """Convert RST species code to MetsiGrow compatible Species."""
    code = internal2mela.species_map[TreeSpecies(spe)].value
    # adjust for merged alders
    return Species(code if code <= 6 else code + 1)

def grow_metsi(input_: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    """
    Wrapper for metsi_grow evolve pipeline. Applies growth step to ForestStand.
    """
    from lukefi.metsi.forestry.naturalprocess.MetsiGrow.grow_metsi import MetsiGrowPredictor
    step = operation_parameters.get('step', 5)
    stand, collected_data = input_
    # build predictor
    pred = MetsiGrowPredictor(stand)
    growth = pred.evolve(step=step)
    # apply deltas
    diameters = [t.breast_height_diameter + d for t, d in zip(stand.reference_trees, growth.trees_id)]
    heights    = [t.height + h for t, h in zip(stand.reference_trees, growth.trees_ih)]
    stems      = [t.stems_per_ha + df for t, df in zip(stand.reference_trees, growth.trees_if)]
    update_stand_growth(stand, diameters, heights, stems, step)
    # prune dead trees
    stand.reference_trees = [t for t in stand.reference_trees if t.stems_per_ha >= 1.0]
    return stand, collected_data