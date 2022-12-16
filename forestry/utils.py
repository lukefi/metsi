from functools import cache
import numpy as np
import csv
import json


@cache
def get_timber_price_table(file_path: str) -> np.ndarray:
    """Converts the string representation of a timber price table csv to a numpy.ndarray."""
    table = np.genfromtxt(file_path, delimiter=';', skip_header=1)
    return table

@cache
def get_renewal_costs_as_dict(file_path: str) -> dict[str, float]:
    """Returns the csv at :file_path: as a dictionary, where key is the operation name and value ie the cost."""
    costs = {}
    with open(file_path, "r") as f:
        reader = csv.reader(f, delimiter=';')
        _ = next(reader)  # skip header
        for row in reader:
            costs[row[0]] = float(row[1]) # operation: cost
    return costs
    
@cache
def get_land_values_as_dict(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)

def update_stand_growth(stand, diameters, heights, stems, step):
    """In-place update stand's reference trees with given diameters, heights and stem count.
    Increase ages for trees and stand. Remove sapling flag from trees that have grown beyond 1.3m. """
    for i, t in enumerate(stand.reference_trees):
        height_before_growth = t.height
        t.breast_height_diameter = diameters[i]
        t.height = heights[i]
        t.stems_per_ha = stems[i]
        t.biological_age += step
        if height_before_growth < 1.3 <= t.height:
            t.breast_height_age = t.biological_age
        if t.height >= 1.3 and t.sapling:
            t.sapling = False
    stand.year += step
