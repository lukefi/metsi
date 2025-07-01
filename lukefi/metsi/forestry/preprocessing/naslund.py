""" Module contains forestry domain spesific model functions """
import math
from typing import Optional
from lukefi.metsi.data.enums.internal import TreeSpecies


NASLUND_PINE_OR_OTHER_CONIFEROUS = [
    TreeSpecies.PINE,
    TreeSpecies.ABIES,
    TreeSpecies.BLACK_SPRUCE,
    TreeSpecies.DOUGLAS_FIR,
    TreeSpecies.JUNIPER,
    TreeSpecies.KEDAR,
    TreeSpecies.LARCH,
    TreeSpecies.OTHER_CONIFEROUS,
    TreeSpecies.OTHER_PINE,
    TreeSpecies.OTHER_SPRUCE,
    TreeSpecies.SERBIAN_SPRUCE,
    TreeSpecies.SHORE_PINE,
    TreeSpecies.THUJA,
    TreeSpecies.UNKNOWN_CONIFEROUS,
    TreeSpecies.YEW,
    ]

def naslund_height(diameter: float | None, species: TreeSpecies | None) -> Optional[float]:
    """
    Näslund height model, with parameters from one Siipilehto. As extracted from LueVMI12.py.
    :param diameter: diameter of the tree at 1.3m height
    :param species: species code of the tree in internal TreeSpecies terms
    :return estimated height of the tree in meters or None
    """
    if diameter is not None and diameter > 0:
        # scots pine or other coniferous
        if species in NASLUND_PINE_OR_OTHER_CONIFEROUS:
            height = ((diameter ** 2) / (0.894 + 0.185 * diameter) ** 2) + 1.3
            return round(height, 2)

        # norway spruce
        elif species == TreeSpecies.SPRUCE:
            height = ((diameter ** 3) / (1.811 + 0.308 * diameter) ** 3) + 1.3
            return round(height, 2)

        else:
            height = ((diameter ** 2) / (0.898 + 0.242 * diameter) ** 2) + 1.3
            return round(height, 2)
    else:
        return None


def naslund_correction(species: TreeSpecies, diameter: float, height: float) -> float:
    ''' Height correction coefficient by Naslund height model

        :spe: tree stratum species
        :diameter: tree stratum diameter 
        :height: tree stratum height
        :return: height correction coefficient
    '''
    h_computed = naslund_height(diameter, species)
    return height/h_computed