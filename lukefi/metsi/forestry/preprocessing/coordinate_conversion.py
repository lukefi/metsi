import ctypes as cts
from pathlib import Path
    
# Defining and initialize the external library 
DLL_PATH = Path('lukefi', 'metsi', 'forestry', 'c', 'lib', 'ykjtm35.dll')
DLL = cts.CDLL(DLL_PATH)


def _is_error(flag: int) -> bool:
    return True if flag != 0 else False


def _erts_tm35_to_ykj(u: float, v: float) -> tuple[float, float]:
    """ Convert ERTS-TM35FIN (EPSG:3067) coordinates to YKJ (Yhtenaiskoordinaatisto)
    
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


def convert_location_to_ykj(stand: ForestStand) -> tuple[float, float, float, str]:
    """ Converts current coordinate system of the stand to match the YKJ (EPSG-2393) coordinate system """
    (latitude, longitude, heigh_above_sea_level, crs) = stand.geo_location
    crs = 'EPSG-2393'
    (x, y) = _erts_tm35_to_ykj(latitude, longitude)    
    new_geo_location = (x, y, heigh_above_sea_level, crs)
    return new_geo_location 