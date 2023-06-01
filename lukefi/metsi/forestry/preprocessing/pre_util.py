""" Module contains basic, domain and state spesific utility functions used in preprocessing operations"""
from typing import Optional, Any
from lukefi.metsi.data.model import ReferenceTree, TreeStratum, ForestStand


# ---- basic utils ----

def get_or_default(maybe: Optional[Any], default: Any = None) -> Any:
    return default if maybe is None else maybe


# ---- domain utils ----

def scale_stems_per_ha(trees: list[ReferenceTree], area_factors: tuple[float, float]) -> list[ReferenceTree]:
    """Scale the given ReferenceTree instances with the given area factors based on diameter cutoff at 0.94 dm"""
    for tree in trees:
        factor = area_factors[0] if tree.breast_height_diameter <= 0.94 else area_factors[1]
        tree.stems_per_ha = tree.stems_per_ha * factor
    return trees


# ---- state utils ----

def stratum_needs_diameter(stratum: TreeStratum) -> bool:
    return not stratum.has_diameter() and stratum.has_height_over_130_cm()


def supplement_mean_diameter(stratum: TreeStratum) -> TreeStratum:
    diameter_factor = 1.2
    stratum.mean_diameter = stratum.mean_height * diameter_factor
    return stratum
