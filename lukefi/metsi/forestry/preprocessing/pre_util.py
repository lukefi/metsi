""" Module contains basic, domain and state spesific utility functions used in preprocessing operations"""
from typing import Optional, Any
from lukefi.metsi.data.model import ReferenceTree, TreeStratum, ForestStand


# ---- basic utils ----

def get_or_default(maybe: Optional[Any], default: Any = None) -> Any:
    return default if maybe is None else maybe


# ---- state utils ----

def stratum_needs_diameter(stratum: TreeStratum) -> bool:
    return not stratum.has_diameter() and stratum.has_height_over_130_cm()


def supplement_mean_diameter(stratum: TreeStratum) -> TreeStratum:
    diameter_factor = 1.2
    stratum.mean_diameter = stratum.mean_height * diameter_factor
    return stratum
