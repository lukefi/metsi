import ctypes as cts
from pathlib import Path
from enum import Enum
from lukefi.metsi.data.model import ForestStand


# Defining and initialize the external library 
DLL_PATH = Path('lukefi', 'metsi', 'forestry', 'c', 'lib', 'ykjtm35.dll')
DLL = cts.CDLL(DLL_PATH)


def _is_error(flag: int) -> bool:
    return True if flag == 0 else False


def _erts_tm35_to_ykj(u: float, v: float) -> tuple[float, float]:
    """ Convert ETRS-TM35FIN (EPSG:3067) coordinates to YKJ (Yhtenaiskoordinaatisto)
    
    :param u: latitude coordinate
    :param v: longitude coordinate
    :return YKJ coordinates tuple
    """
    
    # Type initialization for the input
    f = DLL.tm35fin_to_ykj
    f.argtypes = [
        cts.c_double,
        cts.c_double,
        cts.POINTER(cts.c_double),
        cts.POINTER(cts.c_double)
    ]
    f.restype = cts.c_int

    # Pointer initialization (memory allocation)
    x_ptr = cts.c_double()
    y_ptr = cts.c_double()

    # Actual function call that modifies the memory locations
    response = f(u, v, x_ptr, y_ptr)

    # Error handeling
    if _is_error(response):
        print("Error in call function {f} located in {dll}".format(
            f = f.__name__,
            dll = str(DLL_PATH))
        )
    
    # Return actual values of the pointers
    return (x_ptr.value, y_ptr.value)


class CRS(Enum): 
    EPSG_3067 = ('EPSG:3067', 'ERTS-TM35', 'ETRS-TM35FIN') 
    EPSG_2393 = ('EPSG:2393', 'YKJ')

    @property
    def name(self):
        return ':'.join(self._name_.split('_'))


def _is_ykj(crs: str) -> bool:
    return True if crs in CRS.EPSG_2393.value else False


def _is_erts(crs: str) -> bool:
    return True if crs in CRS.EPSG_3067.value else False


def convert_location_to_ykj(stand: ForestStand) -> tuple[float, float, float, str]:
    """ Converts current coordinate system of the stand to match the YKJ (EPSG:2393) coordinate system """
    (latitude, longitude, heigh_above_sea_level, crs) = stand.geo_location
    if _is_ykj(crs):
        # Already in EPSG:2393. No need to convert.
        return stand.geo_location 
    elif _is_erts(crs):
        crs = CRS.EPSG_2393.name
        (x, y) = _erts_tm35_to_ykj(latitude, longitude)    
        new_geo_location = (x, y, heigh_above_sea_level, crs)
        return new_geo_location
    else:
        Exception(
        "Error while converting from {current_crs} to {target_crs}. Check the source crs.\n"
        "We only support {current_crs} as source crs at the moment.".format(
            current_crs = CRS.EPSG_3067.name,
            target_crs = CRS.EPSG_2393.name))
    

__all__ = ['convert_location_to_ykj', 'CRS']