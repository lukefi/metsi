import ctypes as cts
import sys
from pathlib import Path
from enum import Enum
from typing import Optional
from lukefi.metsi.app.utils import MetsiException


def load_library(path):
    """ Load a shared library from the given path, handling compatibility for Python < 3.12. """
    if sys.version_info >= (3, 12):
        return cts.CDLL(path)
    return cts.CDLL(str(path))


# Defining and initialize the external library
LIB_NAME = 'ykjtm35.dll' if sys.platform == "win32" else 'ykjtm35.so'
DLL_PATH = Path('lukefi', 'metsi', 'forestry', 'c', 'lib', LIB_NAME)

try:
    DLL = load_library(DLL_PATH)
except OSError as e:
    print(f"Failed to load {LIB_NAME}: {e}")


def _is_error(flag: int) -> bool:
    return flag == 0


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
        print(f"Error in call function {f.__name__} located in {str(DLL_PATH)}")

    # Return actual values of the pointers
    return (x_ptr.value, y_ptr.value)


class CRS(Enum):
    EPSG_3067 = ('EPSG:3067', 'ERTS-TM35', 'ETRS-TM35FIN')
    EPSG_2393 = ('EPSG:2393', 'YKJ')

    @property
    def name(self):  # pylint: disable=function-redefined, invalid-overridden-method
        return ':'.join(self._name_.split('_'))  # pylint: disable=no-member


def _is_ykj(crs: Optional[str]) -> bool:
    return crs in CRS.EPSG_2393.value


def _is_erts(crs: Optional[str]) -> bool:
    return crs in CRS.EPSG_3067.value


def convert_location_to_ykj(latitude: float, longitude: float, heigh_above_sea_level: Optional[float],
                            crs: Optional[str]) -> tuple[float, float, Optional[float], Optional[str]]:
    """ Converts current coordinate system of the stand to match the YKJ (EPSG:2393) coordinate system """

    if _is_ykj(crs):
        # Already in EPSG:2393. No need to convert.
        return (latitude, longitude, heigh_above_sea_level, crs)
    if _is_erts(crs):
        crs = CRS.EPSG_2393.name
        (x, y) = _erts_tm35_to_ykj(latitude, longitude)
        new_geo_location = (x, y, heigh_above_sea_level, crs)
        return new_geo_location
    raise MetsiException(f"Error while converting from {CRS.EPSG_3067.name} to {CRS.EPSG_2393.name}. "
                         f"Check the source crs.\n We only support {CRS.EPSG_3067.name} "
                         "as source crs at the moment.")


__all__ = ['convert_location_to_ykj', 'CRS']
