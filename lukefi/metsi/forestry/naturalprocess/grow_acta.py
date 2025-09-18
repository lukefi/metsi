from collections import defaultdict
import math
from statistics import median
import numpy as np
import numpy.typing as npt

from lukefi.metsi.data.model import ReferenceTree, TreeSpecies
from lukefi.metsi.data.vector_model import ReferenceTrees


def yearly_diameter_growth_by_species(
    spe: TreeSpecies,
    d: float,
    h: float,
    biological_age_aggregate: float,
    d13_aggregate: float,
    height_aggregate: float,
    dominant_height: float,
    basal_area_total: float
) -> float:
    """ Model source: Acta Forestalia Fennica 163 """
    if spe == TreeSpecies.PINE:
        growth_percent = math.exp(5.4625
                                  - 0.6675 * math.log(biological_age_aggregate)
                                  - 0.4758 * math.log(basal_area_total)
                                  + 0.1173 * math.log(d13_aggregate)
                                  - 0.9442 * math.log(dominant_height)
                                  - 0.3631 * math.log(d)
                                  + 0.7762 * math.log(h))
    else:
        growth_percent = math.exp(6.9342
                                  - 0.8808 * math.log(biological_age_aggregate)
                                  - 0.4982 * math.log(basal_area_total)
                                  + 0.4159 * math.log(d13_aggregate)
                                  - 0.3865 * math.log(height_aggregate)
                                  - 0.6267 * math.log(d)
                                  + 0.1287 * math.log(h))
    return growth_percent


def yearly_height_growth_by_species(
    spe: TreeSpecies,
    d: float,
    h: float,
    biological_age_aggregate: float,
    d13_aggregate: float,
    height_aggregate: float,
    basal_area_total: float
) -> float:
    """ Model source: Acta Forestalia Fennica 163 """
    if spe == TreeSpecies.PINE:
        growth_percent = math.exp(5.4636
                                  - 0.9002 * math.log(biological_age_aggregate)
                                  + 0.5475 * math.log(d13_aggregate)
                                  - 1.1339 * math.log(h))
    else:
        growth_percent = (12.7402
                          - 1.1786 * math.log(biological_age_aggregate)
                          - 0.0937 * math.log(basal_area_total)
                          - 0.1434 * math.log(d13_aggregate)
                          - 0.8070 * math.log(height_aggregate)
                          + 0.7563 * math.log(d)
                          - 2.0522 * math.log(h))
    return growth_percent


def grow_diameter_and_height(
    trees: list[ReferenceTree],
    step: int = 5
) -> tuple[list[float], list[float]]:
    """ Diameter and height growth for trees with height > 1.3 meters. Based on Acta Forestalia Fennica 163. """
    if not trees:
        return [], []
    group = defaultdict(list)
    for i, t in enumerate(trees):
        group[t.species].append(i)
    ds = [t.breast_height_diameter or 0 for t in trees]
    hs = [t.height for t in trees]
    for s in range(step):
        bigh = [h for h in hs if h >= 1.3]
        if bigh:
            hdom = median(bigh)
            gs = [t.stems_per_ha * math.pi * (0.01 * 0.5 * d)**2 for t, d in zip(trees, ds)]
            g = sum(gs)
            for spe, idx in group.items():
                gg = sum(gs[i] for i in idx)
                ag = sum((trees[i].biological_age + s) * gs[i] for i in idx) / gg
                dg = sum(ds[i] * gs[i] for i in idx) / gg
                hg = sum(hs[i] * gs[i] for i in idx) / gg
                for i in idx:
                    if hs[i] >= 1.3:
                        pd = yearly_diameter_growth_by_species(spe, ds[i], hs[i], ag, dg, hg, hdom, g) / 100
                        ph = yearly_height_growth_by_species(spe, ds[i], hs[i], ag, dg, hg, g) / 100
                        ds[i] *= 1 + pd
                        hs[i] *= 1 + ph
        for i, h in enumerate(hs):
            if h < 1.3:
                hs[i] += 0.3
                if hs[i] >= 1.3 and not ds[i]:
                    ds[i] = 1.0
    return ds, hs


yearly_diameter_growth_by_species_vectorized = np.vectorize(yearly_diameter_growth_by_species)
yearly_height_growth_by_species_vectorized = np.vectorize(yearly_height_growth_by_species)


def grow_diameter_and_height_vectorized(trees: ReferenceTrees,
                                        step: int = 5) -> tuple[npt.NDArray[np.float64],
                                                                npt.NDArray[np.float64]]:
    """
    Diameter and height growth for trees with height > 1.3 meters. Based on Acta Forestalia Fennica 163.
    Vector data implementation.
    """
    if trees.size == 0:
        return np.array([]), np.array([])
    ds = trees.breast_height_diameter
    hs = trees.height
    for s in range(step):
        bigh = np.extract(hs >= 1.3, hs)
        if bigh.size > 0:
            hdom = np.median(bigh)
            gs = trees.stems_per_ha * np.pi * (0.01 * 0.5 * ds)**2
            g = np.sum(gs)
            species = np.unique(trees.species)
            for spe in species:
                gg = np.sum(gs, where=trees.species == spe)
                ag = np.sum((trees.biological_age + s) * gs, where=trees.species == spe) / gg
                dg = np.sum(ds * gs, where=trees.species == spe) / gg
                hg = np.sum(hs * gs, where=trees.species == spe) / gg

                condition = (trees.species == spe) & (hs >= 1.3)
                
                pd = yearly_diameter_growth_by_species_vectorized(spe,
                                                                  ds[condition],
                                                                  hs[condition],
                                                                  ag,
                                                                  dg,
                                                                  hg,
                                                                  hdom,
                                                                  g) / 100
                ph = yearly_height_growth_by_species_vectorized(spe,
                                                                ds[condition],
                                                                hs[condition],
                                                                ag,
                                                                dg,
                                                                hg,
                                                                g) / 100
                ds = ds.copy()
                hs = hs.copy()
                ds[condition] = ds[condition] * (1 + pd)
                hs[condition] = hs[condition] * (1 + ph)
                hs[hs < 1.3] += 0.3
                ds[(ds == 0) & (hs >= 1.3)] = 1.0
    return ds, hs
