import unittest
from lukefi.metsi.data.formats.declarative_conversion import Conversion, ConversionMapper
from random import random

class A():
    def __init__(self, a=10):
        self.a = a

class B():
    def __init__(self):
        pass
    
def custom_f(x, y ,z):
    vars = map(int, [x,y,z])
    return sum(vars)

class TestDeclarativeConvertter(unittest.TestCase):
    def test_conversion_mapper(self):
        data_source = ['1','2','3','4','5','6','7','8','9','10']
        declaration_mapping = {
            'VAR1': Conversion(lambda x: int(x)*2, indices=(0,)),
            'VAR2': Conversion(lambda x: x, indices=(1,)),
            'VAR3': Conversion(custom_f, indices=(0, 3, 4)),
            'VAR4': Conversion(lambda x: float(x) if type(x) is not float else x, indices=(3,)),
            'VAR_RANDOM': Conversion(random),
            'VAR_KISSA': Conversion(lambda: "Kissa123"),
            'VAR5_ONLY_A': Conversion(lambda x, obj: int(x) * obj.a, indices=(0,), object_type=A),
            'VAR6_ONLY_A': Conversion(lambda x, obj: int(x) * obj.VAR3, indices=(0,), object_type=A),
            'VAR7_ONLY_B': Conversion(lambda x, _: x, indices=(0,), object_type=B),
        }
        CM = ConversionMapper(declaration_mapping)
        objs = [ A(), B() ]
        result = []
        for o in objs:
            result.append(CM.apply_conversions(o, data_source))
        self.assertEqual(getattr(result[0], 'VAR1'), 2)
        self.assertEqual(getattr(result[1], 'VAR1'), 2)
        self.assertEqual(getattr(result[0], 'VAR2'), '2')
        self.assertEqual(getattr(result[1], 'VAR2'), '2')
        self.assertEqual(getattr(result[0], 'VAR3'), 10)
        self.assertEqual(getattr(result[1], 'VAR3'), 10)
        self.assertEqual(getattr(result[0], 'VAR4'), 4.0)
        self.assertEqual(getattr(result[1], 'VAR4'), 4.0)
        self.assertEqual(hasattr(result[0], 'VAR_RANDOM'), True)
        self.assertEqual(hasattr(result[1], 'VAR_RANDOM'), True)
        self.assertEqual(getattr(result[0], 'VAR_KISSA'), 'Kissa123')
        self.assertEqual(getattr(result[1], 'VAR_KISSA'), 'Kissa123')
        self.assertEqual(getattr(result[0], 'VAR5_ONLY_A'), 10)
        self.assertEqual(hasattr(result[1], 'VAR5_ONLY_A'), False)
        self.assertEqual(getattr(result[0], 'VAR6_ONLY_A'), 10)
        self.assertEqual(hasattr(result[1], 'VAR6_ONLY_A'), False)
        self.assertEqual(hasattr(result[0], 'VAR7_ONLY_B'), False)
        self.assertEqual(getattr(result[1], 'VAR7_ONLY_B'), '1')