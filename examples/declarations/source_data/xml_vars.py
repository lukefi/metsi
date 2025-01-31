from lukefi.metsi.data.formats.declarative_conversion import Conversion

xml_vars = {
    'xml': {
        'XML1': Conversion(lambda x: x*100, (0,))
    }
}