import csv
import json
from functools import cache
import numpy as np


@cache
def get_timber_price_table(file_path: str) -> np.ndarray:
    """Converts the string representation of a timber price table csv to a numpy.ndarray."""
    table = np.genfromtxt(file_path, delimiter=';', skip_header=1)
    return table


@cache
def get_renewal_costs_as_dict(file_path: str) -> dict[str, float]:
    """Returns the csv at :file_path: as a dictionary, where key is the operation name and value ie the cost."""
    costs = {}
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        _ = next(reader)  # skip header
        for row in reader:
            costs[row[0]] = float(row[1])  # operation: cost
    return costs


@cache
def get_land_values_as_dict(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
