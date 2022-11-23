from functools import cache
from typing import Any, Dict, List
import numpy as np
import csv

@cache
def get_timber_price_table(file_path: str) -> np.ndarray:
    """Converts the string representation of a timber price table csv to a numpy.ndarray."""
    table = np.genfromtxt(file_path, delimiter=';', skip_header=1)
    return table

@cache
def get_renewal_costs_as_dict(file_path: str) -> Dict[str, List[Any]]:
    """Returns the csv at :file_path: as a dictionary."""
    costs = {}
    with open(file_path, "r") as f:
        reader = csv.reader(f, delimiter=';')
        _ = next(reader)  # skip header
        for row in reader:
            costs[row[0]] = {"cost_per_ha": float(row[1]), "operation_name": row[2]}
    return costs