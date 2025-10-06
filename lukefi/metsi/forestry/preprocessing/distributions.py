# pylint: disable=invalid-name

""" Module contains distribution based model functions
    - weibull distribution
    - simple height distribution
    - weibull height distribution for sapling stratum and diameter models of generated
      sapling trees
"""
import math
from typing import Optional
from lukefi.metsi.data.model import ReferenceTree, TreeStratum


# ---- Weibull distribution model ----

def weibull_coeffs(diameter: float, basal_area: float, min_diameter: Optional[float] = None) -> tuple:
    """ Weight parameter calcualtions for Weibull distribution formula.

    Notice that min_diameter can be used to override the formulation of weight (a).

    :param diameter: Mean diameter (cm)
    :param basal_area: Basal area
    :param min_diameter: (optional) Should be a value between [0.0, 4.5]
    :return weight coefficients (a, b, c) used in the Weibull distribution calculation
    """
    w1 = min_diameter if min_diameter is not None else (
        math.exp(-1.306454 + (1.154433 * math.log(diameter)) + (math.pow(0.33956, 2) / 2.0)))
    w3 = math.exp(0.64788 - (0.005558 * basal_area) + (0.025530 * diameter) + (math.pow(0.35365, 2) / 2.0))
    w2 = (diameter - w1) / (pow((-math.log(0.5)), (1.0 / w3)))
    w2 = max(w2, 0.0)
    return w1, w2, w3


def weibull(n_samples: int, diameter: float, basal_area: float, height: float,
            min_diameter: Optional[float] = None) -> list[ReferenceTree]:
    """ Computes Stems per hectare and diameter for given number of refernece trees.
        The values are driven from the Weibull distribution.

    :param n_samples: Number of trees to be created
    :param diameter: Average diameter (cm)
    :param basal_area: Basal area
    :param height: Average height (m)
    :param min_diameter: (optional) Minimum diameter used in weight calculation.
                         If given should be a value between [0.0, 4.5].
    :return: Given number of trees containing stems per hectare and diameters (cm) as object instance members.
    """
    (a, b, c) = weibull_coeffs(diameter, basal_area, min_diameter)

    # x-axis upperlimit
    ax = a + b * math.pow(4.60517, (1.0 / c))

    interval = (ax - a) / float(n_samples)
    if interval < 0.0:
        interval = 1.0

    f1 = 0.0
    xx = a
    result = []
    # For each sample pick-up stems per hectare from Weibull distribution
    for _ in range(1, n_samples + 1):
        xx = xx + interval
        computed_diameter = xx - (interval / 2.0)
        if height < 1.3:
            computed_diameter = 0.0

        f = 1 - math.exp(-math.pow(((xx - a) / b), c))

        if xx >= ax:
            f = 1.0

        p = f - f1  # precentual ratio of stems in sample i
        f1 = f

        stems = (12732.4 * basal_area) / math.pow(computed_diameter, 2.0)
        stems_per_sample = p * stems

        reference_tree = ReferenceTree()
        reference_tree.stems_per_ha = stems_per_sample
        reference_tree.breast_height_diameter = computed_diameter

        result.append(reference_tree)
    return result


# ---- Simple height distribution model ----

# NOTE: Debricated, only for test purposes
def simple_height_distribution(stratum: TreeStratum, n_trees: int) -> list[ReferenceTree]:
    """ Generate N trees from tree stratum.

    For a single tree, height and diameter are obtained from stratum.
    The stem count for single reference tree is the fraction of stratums total stem count.
    NOTE: that the stem count for all trees is even.
    NOTE: for testing and alternative for sapling weibull distributions
    """
    stems_per_tree = stratum.stems_per_ha / n_trees
    result = []
    for _ in range(n_trees):
        reference_tree = ReferenceTree()
        reference_tree.height = stratum.mean_height
        reference_tree.breast_height_diameter = stratum.mean_diameter
        reference_tree.stems_per_ha = stems_per_tree
        result.append(reference_tree)
    return result


# ---- Weibull height distribution models for diameter models of sapling trees ----

def diameter_model_valkonen(height_rt: float) -> float:
    """ Sapling diameter prediction model by Valkonen (1997).
    Predicts sapling diameter for youngest trees directly from height.

    height_rt: reference tree height (m)
    return: reference tree diameter (cm)
    """
    lndi = 1.5663 + 0.4559 * math.log(height_rt) + 0.0324 * height_rt
    return math.exp(lndi + 0.004713 / 2) - 5.0


def diameter_model_siipilehto(height_rt: float, height: float, diameter: float, dominant_height: float) -> float:
    """ Diameter model for reference tree by Siipilehto in FORECO 257

    height_rt: Reference tree height (m)
    height: Mean diameter of stratum (cm)
    diameter: Mean diameter of stratum (cm)
    dominant_height: Stand dominant height (m)
    return: reference tree diameter (cm)
    """
    lndiJS = (
        0.3904
        + 0.9119 * math.log(height_rt - 1.0)
        + 0.05318 * height_rt
        - 1.0845 * math.log(height)
        + 0.9468 * math.log(diameter + 1)
        - 0.0311 * dominant_height
    )
    dvari = 0.000478 + 0.000305 + 0.03199  # for bias correction
    return math.exp(lndiJS + dvari / 2.0)


def predict_sapling_diameters(
        reference_trees: list[ReferenceTree],
        height: float,
        diameter: float,
        dominant_height: float) -> list[ReferenceTree]:
    """ Logic for predicting sapling diameters.

    Diameters are predicted via Valkonen's diameter height model or Siipilehto's diameter model.
    For other cases diameter is set to zero.

    reference_trees: list of reference trees with height and stems_per_ha members inflated
    height: Mean height of stratum (m)
    diameter: Mean diameter of stratum (cm)
    return: Updated list of reference trees containing diameters (cm).
    """
    for rt in reference_trees:
        if rt.has_height_over_130_cm() and height > 1.3 and diameter:
            di = diameter_model_siipilehto(
                rt.height,
                height,
                diameter,
                dominant_height
            )
        elif rt.height >= 1.3 and (height >= 1.3 or not diameter):
            di = diameter_model_valkonen(rt.height)
        else:
            # rt.height <= 1.3 and other cases
            di = 0.0
        rt.breast_height_diameter = di
    return reference_trees


def weibull_sapling(height: float, stem_count: float, dominant_height: float, n_trees: int) -> list[ReferenceTree]:
    """Formulates weibull height distribution of sapling stratum and the number of stems of the trees

    References: Siipilehto, J. 2009, Modelling stand structure in young Scots pine dominated stands.
        Forest Ecology and management 257: 223–232. (GLM model).

    height: Average height of stratum (m)
    stem_count: Stratum stem count
    dominant_height: Dominant height
    n_trees: Number of reference trees to be generated
    return: Given number of trees with stems per hectar and height (m) properties inflated.
    """

    # Mean diameter and dominant height can be illogical:
    if dominant_height <= height:
        dominant_height = 1.05 * height

    Ph = 0
    Nh = 0

    # Weibull parameters Generalized Linear Model (look Cao 2004)
    # With GLM model, fitting the distribution to treewise data and
    # the solution of parameters of the prediction model are done at the same time
    a = 0.0

    b0 = 0.1942
    b1 = 0.9971
    b2 = -0.0580

    c0 = -2.4203
    c1 = 0.0895
    c2 = -0.0637
    c3 = 0.2510
    c4 = 1.2707

    # KHar Error correction: Siipilehto 2009, Forest ecology...  p. 8, formula 6
    # Height must be logarithmic.
    b = math.exp(b0
                 + b1 * math.log(height)
                 + b2 / math.log(dominant_height / height + 0.4)
                 )
    c = math.exp(
        c0
        + c1 * height
        + c2 * dominant_height
        + c3 * math.log(stem_count)
        + c4 / math.log(dominant_height / height + 0.4)
    )

    # Weibull height distribution is known, trees are picked up from the distribution
    classN = 1 / float(n_trees)    # stem number from class border
    Nh = stem_count / float(n_trees)        # frequency
    classH = classN / 2          # for the class center
    result = []

    for i in range(n_trees):
        reference_tree = ReferenceTree()
        Ph = float(i + 1) * classN - classH         # class center
        # picking up height from the cumulative Weibull distribution. Analytical solution.
        hi = b * (-math.log(1.0 - Ph))**(1.0 / c) + a
        reference_tree.height = round(hi, 2)

        reference_tree.stems_per_ha = Nh
        reference_tree.sapling = True
        result.append(reference_tree)
    return result


def sapling_height_distribution(stratum: TreeStratum, dominant_height: float, n_trees: int) -> list[ReferenceTree]:
    """Formulates height distribution of sapling stratum and predicts the diameters and the number of stems of the
    simulation trees
    References: Siipilehto, J. 2009, Modelling stand structure in young Scots pine dominated stands.
                Forest Ecology and management 257: 223–232. (GLM model)

    return: Given number of trees containing breast height diameter (cm), height (m) and stems per hectar
    """
    if n_trees == 1:
        # single tree:
        reference_tree = ReferenceTree()
        reference_tree.breast_height_diameter = stratum.mean_diameter
        reference_tree.height = stratum.mean_height
        reference_tree.stems_per_ha = stratum.stems_per_ha
        return [reference_tree]
    # more than one trees
    result = weibull_sapling(
        stratum.mean_height,
        stratum.stems_per_ha,
        dominant_height,
        n_trees
    )
    dominant_height = 1.05 * stratum.mean_height
    return predict_sapling_diameters(
        result,
        stratum.mean_height,
        stratum.mean_diameter,
        dominant_height
    )
