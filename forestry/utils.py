from functools import cache
from io import StringIO
import numpy as np

@cache
def get_timber_price_table(csv_string: str) -> np.ndarray:
    """Converts the string representation of a timber price table csv to a numpy.ndarray."""
    table = np.genfromtxt(StringIO(csv_string), delimiter=';', skip_header=1)
    return table