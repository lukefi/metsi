""" An control file example to demonstrate to usage on declarative variables and exportin of the suchs variables """

from lukefi.metsi.data.formats.declarative_conversion import Conversion
from lukefi.metsi.data.model import ForestStand, TreeStratum
from math import pow
from random import random
from examples.declarations.export_prepro import mela


def sum3(x, y, z) -> float:
    return float(x) + float(y) + float(z)


control_structure = {
    "app_configuration": {
        "state_format": "vmi13",
        "run_modes": ["preprocess", "export_prepro"]
    },
    # Examples of declarative conversions
    "conversions": {
        'vmi13': {
            # common conversions
            'VAR0': Conversion(lambda: 123456789),
            'VAR1': Conversion(lambda x: int(x)*2, indices=(0,)),
            'VAR2': Conversion(lambda x: x, indices=(1,)),
            'VAR3': Conversion(lambda x,y,z: sum3(x,y,z), indices=(2, 3, 4)),
            'VAR4': Conversion(lambda x, y: pow(int(x), int(y)), indices=(2, 5)),
            'VAR5': Conversion(lambda x, y: pow(float(x), float(y)), indices=(3, 5)),
            'VAR_RANDOM': Conversion(random),
            'VAR_KISSA': Conversion(lambda: "Kissa123"),
            'VAR8': Conversion(lambda x: str(x) if type(x) is not str else x, indices=(3,)),
            # conversions based on object type spesifications
            'VAR9': Conversion(lambda x, obj: int(x) * obj.area, indices=(0,), object_type=ForestStand),
            'VAR10': Conversion(lambda x, obj: int(x) * obj.VAR1, indices=(0,), object_type=ForestStand),
            'VAR11': Conversion(lambda x, obj: int(x) * obj.VAR1, indices=(0,), object_type=TreeStratum),
        }
    }
}

# The preprocessing export format is added as an external module
control_structure['export_prepro'] = {}
control_structure['export_prepro'].update(mela) # includes declared variables + mela format spesific operands

__all__ = ['control_structure']