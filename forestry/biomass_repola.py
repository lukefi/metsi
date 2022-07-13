import math
from forestdatamodel.model import ForestStand, ReferenceTree


# Sources
# Repola J. (2013). Modelling tree biomasses in Finland
# https://dissertationesforestales.fi/pdf/article1941.pdf
# Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland
# https://www.silvafennica.fi/pdf/article184.pdf
# Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland
# https://www.silvafennica.fi/pdf/article236.pdf

# Models 1-3 inputs:
# d = tree diameter at breast height, cm
# h = tree height, m
# ---------------------------------------
# Models 2-3 inputs:
# cl = length of living crown, m
# cr = crown ratio, 0-1
# t = tree age at breast height
# -------------------------------------------------------
# Model 3 inputs (no functions yet for these):
# ig5 = cross-sectional area increment at breast height during the last five years (cm^2)
# i5 = brest height radial increment during the last five years (cm, *mm for birch)
# bt = double bark thickness at breat height (cm)

def stump_diameter(tree: ReferenceTree) -> float:
    """
    Laasasenaho 1975, stump diameter f(d):
    Needed in biomass calculations
    """
    return 2.0 + 1.25 * tree.breast_height_diameter


def stem_wood_biomass_vol_1(tree: ReferenceTree, stand: ForestStand, treevolume) -> list:
    """
    Returns list: stem wood, stem bark
    """
    if tree.species == 1:
        stem_with_bark_bm = treevolume * (
                    378.39 - 78.829 * tree.breast_height_diameter / tree.breast_height_age + 0.039 * stand.degree_days)
    elif tree.species == 2:
        stem_with_bark_bm = treevolume * (442.03 - 0.904 * stump_diameter(
            tree) - 82.695 * tree.breast_height_diameter / tree.breast_height_age)
    else:
        stem_with_bark_bm = treevolume * (431.43 + 28.054 * math.log(
            stump_diameter(tree)) - 52.203 * tree.breast_height_diameter / tree.breast_height_age)
    stem_bark = (stem_bark_biomass_1(tree) / (
                stem_wood_biomass_1(tree) + stem_bark_biomass_1(tree))) * stem_with_bark_bm
    stem_wood = (stem_wood_biomass_1(tree) / (
                stem_wood_biomass_1(tree) + stem_bark_biomass_1(tree))) * stem_with_bark_bm
    return [stem_wood / 1000, stem_bark / 1000]


def stem_wood_biomass_vol_2(tree: ReferenceTree, stand: ForestStand, treevolume, treevolumewaste) -> list:
    """
    Returns list: stem with bark, stem wood with bark, stem waste with bark
    """
    if tree.species == 1:
        stem_with_bark_bm = treevolume * (
                    378.39 - 78.829 * tree.breast_height_diameter / tree.breast_height_age + 0.039 * stand.degree_days)
    elif tree.species == 2:
        stem_with_bark_bm = treevolume * (442.03 - 0.904 * stump_diameter(
            tree) - 82.695 * tree.breast_height_diameter / tree.breast_height_age)
    else:
        stem_with_bark_bm = treevolume * (431.43 + 28.054 * math.log(
            stump_diameter(tree)) - 52.203 * tree.breast_height_diameter / tree.breast_height_age)
    stem_waste = (treevolumewaste / treevolume) * stem_with_bark_bm
    stem_wood = stem_with_bark_bm - stem_waste
    return [stem_with_bark_bm / 1000, stem_wood / 1000, stem_waste / 1000]


def stem_wood_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2013). Modelling tree biomasses in Finland, p. 25
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -3.721 + 8.103 * (stump_diameter(tree) / (stump_diameter(tree) + 14)) + 5.066 * (
                    tree.height / (tree.height + 12)) + (0.002 + 0.009) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -3.555 + 8.042 * (stump_diameter(tree) / (stump_diameter(tree) + 14)) + 0.869 * math.log(
            tree.height) + 0.015 * tree.height + (0.009 + 0.009) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -4.879 + 9.651 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + 1.012 * math.log(tree.height) + (
                    0.00263 + 0.00544) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Stem wood biomass f(d,h,t)
def stem_wood_biomass_2(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 641-645
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 621-623
    """
    cl = tree.height - tree.lowest_living_branch_height
    if tree.species == 1:  # Scots Pine
        lnbm = -4.018 + 8.358 * (stump_diameter(tree) / (stump_diameter(tree) + 14)) + 4.646 * (
                    tree.height / (tree.height + 10)) + 0.041 * math.log(tree.breast_height_age) + (0.001 + 0.008) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -4.000 + 8.881 * stump_diameter(tree) / (stump_diameter(tree) + 12) + 0.728 * math.log(
            tree.height) + 0.022 * tree.height - 0.273 * stump_diameter(tree) / tree.breast_height_age + (
                           0.003 + 0.008) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -4.886 + 9.965 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + 0.966 * math.log(
            tree.height) - 0.135 * tree.breast_height_diameter / tree.breast_height_age + (0.002 + 0.005) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Stem bark biomass 1 #f(d,h)
def stem_bark_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 631-633
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 611-613
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -4.548 + 7.997 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + 0.357 * (
            math.log(tree.height)) + (0.015 + 0.061) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -4.548 + 9.448 * (stump_diameter(tree) / (stump_diameter(tree) + 18)) + 0.436 * (
            math.log(tree.height)) + (0.023 + 0.041) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -5.401 + 10.061 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + 2.657 * (
                    tree.height / (tree.height + 20)) + (0.01043 + 0.04443) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Stem bark biomass 2 f(d,h,cr)
def stem_bark_biomass_2(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 641-645
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 621-623
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -4.695 + 8.727 * (stump_diameter(tree) / (stump_diameter(tree) + 14)) + 0.357 * math.log(tree.height) + (
                    0.014 + 0.057) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -4.437 + 10.071 * (stump_diameter(tree) / (stump_diameter(tree) + 18)) + 0.261 * (
            math.log(tree.height)) + (0.019 + 0.039) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -5.433 + 10.121 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + 2.647 * (
                    tree.height / (tree.height + 20)) + (0.011 + 0.0044) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Living branches biomass 1 f(d,f)
def living_branches_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 631-633
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 611-613
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -6.162 + 15.075 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) - 2.618 * (
                    tree.height / (tree.height + 12)) + (0.041 + 0.089) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -4.214 + 14.508 * (stump_diameter(tree) / (stump_diameter(tree) + 13)) - 3.277 * (
                    tree.height / (tree.height + 5)) + (0.039 + 0.081) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -4.152 + 15.874 * (stump_diameter(tree) / (stump_diameter(tree) + 16)) - 4.407 * (
                    tree.height / (tree.height + 10)) + (0.02733 + 0.07662) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Living branches biomass 2 f(d,h,cr)
def living_branches_biomass_2(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 641-645
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 621-623
    """
    cl = tree.height - tree.lowest_living_branch_height
    if tree.species == 1:  # Scots Pine
        lnbm = -5.224 + 13.022 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) - 4.867 * (
                    tree.height / (tree.height + 8)) + 1.058 * math.log(cl) + (0.02 + 0.067) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -2.945 + 12.698 * (stump_diameter(tree) / (stump_diameter(tree) + 14)) - 6.183 * (
                    tree.height / (tree.height + 5)) + 0.959 * math.log(cl) + (0.013 + 0.072) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -4.837 + 13.222 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) - 4.639 * (
                    tree.height / (tree.height + 12)) + 0.135 * cl + (0.013 + 0.054) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Dead branches biomass 1 f(d,h)
def dead_branches_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 631-633
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 611-613
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -5.201 + 10.574 * (stump_diameter(tree) / (stump_diameter(tree) + 16))
        bm = math.exp(lnbm)
        bm = bm * 0.911
    elif tree.species == 2:  # Norway Spruce
        lnbm = -4.850 + 7.702 * (stump_diameter(tree) / (stump_diameter(tree) + 18)) + 0.513 * (math.log(tree.height))
        bm = math.exp(lnbm)
        bm = bm * 1.343
    else:  # Others, model for Birch
        lnbm = -8.335 + 12.402 * (stump_diameter(tree) / (stump_diameter(tree) + 16))
        bm = math.exp(lnbm)
        bm = bm * 2.0737
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Dead branches biomass 2 f(d,h,cr)
def dead_branches_biomass_2(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 641-645
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 621-623
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -5.318 + 10.771 * (stump_diameter(tree) / (stump_diameter(tree) + 16))
        bm = math.exp(lnbm) * 0.913
    elif tree.species == 2:  # Norway Spruce
        lnbm = -5.317 + 6.384 * (stump_diameter(tree) / (stump_diameter(tree) + 18)) + 0.982 * math.log(tree.height)
        bm = math.exp(lnbm) * 1.208
    else:  # Others, model for Birch
        lnbm = -7.996 + 11.824 * (stump_diameter(tree) / (stump_diameter(tree) + 16))
        bm = math.exp(lnbm) * 2.1491
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Dead branches biomass 2b f(d,h,cr)
def dead_branches_biomass_2b(tree: ReferenceTree) -> float:
    if tree.species == 1:  # Scots Pine
        lnbm = -5.334 + 10.789 * (stump_diameter(tree) / (stump_diameter(tree) + 16))
        bm = math.exp(lnbm) * 1.242
    elif tree.species == 2:  # Norway Spruce
        lnbm = -5.467 + 6.252 * (stump_diameter(tree) / (stump_diameter(tree) + 18)) + 1.068 * math.log(tree.height)
        bm = math.exp(lnbm) * 1.181
    else:  # Others, model for Birch
        lnbm = -7.742 + 11.362 * (stump_diameter(tree) / (stump_diameter(tree) + 16))
        bm = math.exp(lnbm) * 2.245
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Foliage/needles biomass 1 f(d,h)
def foliage_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 631-633
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 611-613
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -6.303 + 14.472 * (stump_diameter(tree) / (stump_diameter(tree) + 6)) - 3.976 * (
                    tree.height / (tree.height + 1)) + (0.109 + 0.118) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -2.994 + 12.251 * (stump_diameter(tree) / (stump_diameter(tree) + 10)) - 3.415 * (
                    tree.height / (tree.height + 1)) + (0.107 + 0.089) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -29.566 + 33.372 * (stump_diameter(tree) / (stump_diameter(tree) + 2)) + (0.00 + 0.077) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Foliage/needles biomass 2 f(d,h,cr)
def foliage_biomass_2(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 641-645
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 621-623
    """
    cl = tree.height - tree.lowest_living_branch_height
    cr = (tree.height - tree.lowest_living_branch_height) / tree.height
    if tree.species == 1:  # Scots Pine
        lnbm = -1.748 + 14.824 * (stump_diameter(tree) / (stump_diameter(tree) + 4)) - 12.684 * (
                    tree.height / (tree.height + 1)) + 1.209 * math.log(cl) + (0.032 + 0.093) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -0.085 + 15.222 * (stump_diameter(tree) / (stump_diameter(tree) + 4)) - 14.446 * (
                    tree.height / (tree.height + 1)) + 1.273 * math.log(cl) + (0.028 + 0.087) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -20.856 + 22.320 * (stump_diameter(tree) / (stump_diameter(tree) + 2)) + 2.819 * cr + (0.011 + 0.044) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Foliage/needles biomass 2b f(d,h,cr)
def foliage_biomass_2b(tree: ReferenceTree) -> float:
    cl = tree.height - tree.lowest_living_branch_height
    cr = (tree.height - tree.lowest_living_branch_height) / tree.height
    if tree.species == 1:  # Scots Pine
        lnbm = -2.385 + 15.022 * (stump_diameter(tree) / (stump_diameter(tree) + 4)) - 11.979 * (
                    tree.height / (tree.height + 1)) + 1.116 * math.log(cl) + (0.034 + 0.095) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = 0.286 + 16.286 * (stump_diameter(tree) / (stump_diameter(tree) + 4)) - 15.576 * (
                    tree.height / (tree.height + 1)) + 1.17 * math.log(cl) + (0.021 + 0.09) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -20.856 + 22.320 * (stump_diameter(tree) / (stump_diameter(tree) + 2)) + 2.819 * cr + (0.011 + 0.044) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Stump biomass f(d,h)
def stump_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 631-633
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 611-613
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -6.753 + 12.681 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + (0.010 + 0.044) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -3.964 + 11.730 * (stump_diameter(tree) / (stump_diameter(tree) + 26)) + (0.065 + 0.058) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -3.574 + 11.304 * (stump_diameter(tree) / (stump_diameter(tree) + 26)) + (0.02154 + 0.04542) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Stump biomass 1b f(d,h)
def stump_biomass_1b(tree: ReferenceTree) -> float:
    if tree.species == 1:  # Scots Pine
        lnbm = -6.739 + 12.658 * (stump_diameter(tree) / (stump_diameter(tree) + 12)) + (0.009 + 0.044) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -3.962 + 11.725 * (stump_diameter(tree) / (stump_diameter(tree) + 26)) + (0.065 + 0.058) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -3.677 + 11.537 * (stump_diameter(tree) / (stump_diameter(tree) + 26)) + (0.021 + 0.046) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Coarse roots (>1cm) biomass 1 f(d,h)
def roots_biomass_1(tree: ReferenceTree) -> float:
    """
    Repola J. (2009) Silva Fennica 43(4) Biomass equations for Scots pine and Norway spruce in Finland p. 631-633
    Repola J. (2008) Silva Fennica 42(4) Biomass equations for birch in Finland p. 611-613
    """
    if tree.species == 1:  # Scots Pine
        lnbm = -5.550 + 13.408 * (stump_diameter(tree) / (stump_diameter(tree) + 15)) + (0.000 + 0.079) / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -2.294 + 10.646 * (stump_diameter(tree) / (stump_diameter(tree) + 24)) + (0.105 + 0.114) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -3.223 + 6.497 * (stump_diameter(tree) / (stump_diameter(tree) + 22)) + 1.033 * math.log(tree.height) + (
                    0.048 + 0.02677) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


# Coarse roots (>1cm) 1b f(d,h)
def roots_biomass_1b(tree: ReferenceTree) -> float:
    if tree.species == 1:  # Scots Pine
        lnbm = -5.6 + 13.49 * (stump_diameter(tree) / (stump_diameter(tree) + 15)) + 0.077 / 2
        bm = math.exp(lnbm)
    elif tree.species == 2:  # Norway Spruce
        lnbm = -2.295 + 10.649 * (stump_diameter(tree) / (stump_diameter(tree) + 24)) + (0.105 + 0.114) / 2
        bm = math.exp(lnbm)
    else:  # Others, model for Birch
        lnbm = -3.183 + 7.204 * (stump_diameter(tree) / (stump_diameter(tree) + 22)) + 0.892 * math.log(tree.height) + (
                    0.047 + 0.027) / 2
        bm = math.exp(lnbm)
    # bm = Biomass of component, kg
    # to tons:
    bm = bm / 1000
    return bm


def tree_biomass(tree: ReferenceTree, stand: ForestStand, volume, volumewaste, models) -> list:
    """
    list of tree biomass weights in tons by biomass component
    Models: 1: Repola f(d,h), 2: Repola f(d,h,cr), 
    3: Repola f(d,h,cr) components like MOTTI, 
    4: Repola f(d,h,cr) components like MELA
    MODELS=1-3: stem wood, stem bark, living branches, dead branches, foliage, stump roots
    MODELS=4: stem w bark, stem merchantable wood, stem waste, living branches, dead branches, foliage, stump roots 
    input vol used only if MODELS=3|4, input volwaste used only if MODELS=3
    """
    biomass_components = [0, 0, 0, 0, 0, 0, 0, 0]
    if models == 1:
        biomass_components[0] = stem_wood_biomass_1(tree)
        biomass_components[1] = stem_bark_biomass_1(tree)
        biomass_components[2] = living_branches_biomass_1(tree)
        biomass_components[3] = dead_branches_biomass_1(tree)
        biomass_components[4] = foliage_biomass_1(tree)
        biomass_components[5] = stump_biomass_1(tree)
        biomass_components[6] = roots_biomass_1(tree)
    elif models == 2:
        biomass_components[0] = stem_wood_biomass_2(tree)
        biomass_components[1] = stem_bark_biomass_2(tree)
        biomass_components[2] = living_branches_biomass_2(tree)
        biomass_components[3] = dead_branches_biomass_2(tree)
        biomass_components[4] = foliage_biomass_2(tree)
        biomass_components[5] = stump_biomass_1(tree)
        biomass_components[6] = roots_biomass_1(tree)
    elif models == 3:
        stem = stem_wood_biomass_vol_2(tree, stand, volume, volumewaste)
        biomass_components[0] = stem[0]
        biomass_components[1] = stem[1]
        biomass_components[2] = stem[2]
        biomass_components[3] = living_branches_biomass_2(tree)
        biomass_components[4] = dead_branches_biomass_2b(tree)
        biomass_components[5] = foliage_biomass_2(tree)
        biomass_components[6] = stump_biomass_1b(tree)
        biomass_components[7] = roots_biomass_1b(tree)
    else:
        stem = stem_wood_biomass_vol_1(tree, stand, volume)
        biomass_components[0] = stem[0]
        biomass_components[1] = stem[1]
        biomass_components[2] = living_branches_biomass_2(tree)
        biomass_components[3] = dead_branches_biomass_1(tree)
        biomass_components[4] = foliage_biomass_2b(tree)
        biomass_components[5] = stump_biomass_1(tree)
        biomass_components[6] = roots_biomass_1(tree)
    return biomass_components


def small_tree_biomass(tree: ReferenceTree, stand: ForestStand, volume, volumewaste, models) -> list:
    """
    list of tree biomass weights in tons by biomass component
    Models: 1: Repola f(d,h), 2: Repola f(d,h,cr), 
    3: Repola f(d,h,cr) components like MOTTI, 
    4: Repola f(d,h,cr) components like MELA
    MODELS=1-3: stem wood, stem bark, living branches, dead branches, foliage, stump roots
    MODELS=4: stem w bark, stem merchantable wood, stem waste, living branches, dead branches, foliage, stump roots 
    input vol used only if MODELS=3|4, input volwaste used only if MODELS=3
    """
    reference_tree = ReferenceTree()
    reference_tree.species = tree.species
    reference_tree.breast_height_diameter = tree.breast_height_diameter
    if reference_tree.breast_height_diameter == 0:
        reference_tree.breast_height_diameter = 0.1
    reference_tree.height = 1.3
    minimum_model_tree_biomass = tree_biomass(reference_tree, stand, volume, volumewaste, models)
    coef = tree.height / reference_tree.height
    small_tree_bm = [x * coef for x in minimum_model_tree_biomass]
    return small_tree_bm


def biomasses_by_component_stand(stand: ForestStand, treevolumes, wastevolumes, models) -> list:
    biomass_components = [0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(0, len(stand.reference_trees)):
        tree = stand.reference_trees[i]
        if tree.height >= 1.3:
            tree_biomasses = tree_biomass(tree, stand, treevolumes[i], wastevolumes[i], models)
            tree_x_stemcount = [x * tree.stems_per_ha for x in tree_biomasses]
            biomass_components = [x1 + x2 for x1, x2 in zip(biomass_components, tree_x_stemcount)]
        else:
            tree_biomasses = small_tree_biomass(tree, stand, treevolumes[i], wastevolumes[i], models)
            tree_x_stemcount = [x * tree.stems_per_ha for x in tree_biomasses]
            biomass_components = [x1 + x2 for x1, x2 in zip(biomass_components, tree_x_stemcount)]
    return biomass_components
