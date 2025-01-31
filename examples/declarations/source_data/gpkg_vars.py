from lukefi.metsi.data.formats.declarative_conversion import Conversion

gpkg_vars = {
    'gpkg': {
        'GPKG1': Conversion(lambda x: x*100, (0,))
    }
}