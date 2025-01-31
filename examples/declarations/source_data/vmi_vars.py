from lukefi.metsi.data.formats.declarative_conversion import Conversion
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.data.formats.vmi_const import VMI13StandIndices, VMI12StandIndices
from lukefi.metsi.data.formats.vmi_util import parse_vmi13_date, parse_vmi12_date
from math import pow
from random import random

def sum3(x,y,z):
    return int(x)+int(y)+int(z)


# NO EIHÄN NÄITÄ KANNATA LAITAA KUN ON IHAN DUMMY ESIMERKKI JA TESTEISSÄ ON SAMANLAINEN
# KYSY REETALTA OIKEINTA ESIMERKKEJÄ TAI TEE YKSI YHDISTÄMÄLLÄ CONVERSION(VMI INDICES JA VMI CONV)

vmi_vars = {
    'vmi13': {
        # 'DATE': Conversion(parse_vmi13_date, VMI13StandIndices.date)
        # common conversions
        'VAR0': Conversion(lambda: 123456789),
        'VAR1': Conversion(lambda x: int(x)*2, indices=(0,)),
        'VAR2': Conversion(lambda x: x, indices=(1,)),
        'VAR3': Conversion(sum3, indices=(2, 3, 4)),
        'VAR4': Conversion(lambda x, y: pow(int(x), int(y)), indices=(2, 5)),
        'VAR5': Conversion(lambda x, y: pow(float(x), float(y)), indices=(3, 5)),
        'VAR_RANDOM': Conversion(random),
        'VAR_KISSA': Conversion(lambda: "Kissa123"),
        'VAR8': Conversion(lambda x: str(x) if type(x) is not str else x, indices=(3,)),
        # conversions based on object type spesifications
        'VAR9': Conversion(lambda x, obj: int(x) * obj.area, indices=(0,), object_type=ForestStand),
        'VAR10': Conversion(lambda x, obj: int(x) * obj.VAR1, indices=(0,), object_type=ForestStand),
        'VAR11': Conversion(lambda x, obj: int(x) * obj.VAR1, indices=(0,), object_type=TreeStratum),
    },
    'vmi12': {
        # 'DATE': Conversion(parse_vmi12_date, VMI12StandIndices.date)
        'VAR0': Conversion(lambda: 123456789),
        'VAR1': Conversion(lambda x: x, indices=[slice(0,5)]),
        'VAR2': Conversion(lambda x: x.upper(), indices=[slice(0,5)]),
        'VAR_RANDOM': Conversion(random),
    },
}