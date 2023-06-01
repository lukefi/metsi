from collections.abc import Callable, Sequence
import numpy as np
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.forestry.cross_cutting import stem_profile
from lukefi.metsi.forestry.cross_cutting.cross_cutting_fhk import cross_cut_fhk
from lukefi.metsi.forestry.cross_cutting.cross_cutting_lupa import cross_cut_lupa

_cross_cut_species_mapper = {
    TreeSpecies.PINE: "pine",
    TreeSpecies.SPRUCE: "spruce",
    TreeSpecies.CURLY_BIRCH: "birch",
    TreeSpecies.DOWNY_BIRCH: "birch",
    TreeSpecies.SILVER_BIRCH: "birch"
}

ZERO_DIAMETER_DEFAULTS = ([3], [0.000045], [20])  # energy wood, m3, €/m3; values from Reijo Mykkänen
CrossCutFn = Callable[..., tuple[Sequence[int], Sequence[float], Sequence[float]]]


def apteeraus_Nasberg(T: np.ndarray, P: np.ndarray, m: int, n: int, div: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    This function has been ported from, and should be updated according to, the R implementation.
    """
    V = np.zeros(n)
    C = np.zeros(n)
    A = np.zeros(n)
    L = np.zeros(n)

    t = 1
    d_top = 0.0
    d_min = 0.0
    v = 0.0
    c = 0.0
    v_tot = 0.0
    c_tot = 0.0

    for i in range(n): #iterate over div-length segmnents of the tree trunk
        for j in range(m): #iterate over the number of timber assortment price classes (row count in puutavaralajimaarittelyt.txt)
            # numpy array indexing: 1st row 2nd element: arr[0, 1]
            # in R it's the same order: arr[2, 3] --> the item on 2nd row and 3rd column
            # but whereas R-indexing is one-based, Python's is zero-based --> indexing has been offset by one
            t = int(i + P[j,2] / div)
            if t < n:
                d_top = T[t,0]
                d_min = P[j, 1]

                if d_top >= d_min:
                    v = T[t,2] - T[i,2]
                    c = v * P[j, 3]
                    v_tot = v + V[i]
                    c_tot = c + C[i]

                    if c_tot > C[t]:
                        V[t] = v_tot
                        C[t] = c_tot
                        A[t] = P[j, 0]
                        L[t] = i

    maxi = np.argmax(C)

    nas = np.unique(P[:, 0])

    volumes = np.zeros(len(nas))
    values = np.zeros(len(nas))

    a = l = 1

    while maxi > 0:
        a = int(A[maxi])-1 # a is used as an index for volumes and values. Here in Python, it must be subtracted by one to work with zero-based indexing.
        l = int(L[maxi])
        volumes[a] = volumes[a] + V[maxi] - V[l]
        values[a] = values[a] + C[maxi] - C[l]

        maxi = l

    return (nas, volumes, values) #deviating from the R implementation a little bit by also returning `nas`, the list of unique timber grades.


def cross_cut_py(timber_price_table, div = 10) -> CrossCutFn:
    def cc(species: TreeSpecies, breast_height_diameter, height):
        species_string = _cross_cut_species_mapper.get(species, "birch") #birch is used as the default species in cross cutting
        #the original cross-cut scripts rely on the height being an integer, thus rounding.
        height = round(height)
        n = int((height*100)/div-1)
        T = stem_profile.create_tree_stem_profile(species_string, breast_height_diameter, height, n)
        P = timber_price_table
        m = P.shape[0]

        return apteeraus_Nasberg(T, P, m, n, div)
    return cc


def cross_cut(
        species: TreeSpecies,
        breast_height_diameter: float,
        height: float,
        P: np.ndarray,
        div=10,
        impl: str = "py"
        ) -> tuple[Sequence[int], Sequence[float], Sequence[float]]:
    """
    Returns a tuple containing unique timber grades and their respective volumes and values.
    If :breast_height_diameter: is 0 or none, the Nasberg cross-cutting algorithm can't be applied.
    In this case, returns hardcoded constants.
    """
    if breast_height_diameter is not None and breast_height_diameter < 0:
        raise ValueError("breast_height_diameter must be a non-negative number")
    if breast_height_diameter in (None, 0):
        return ZERO_DIAMETER_DEFAULTS
    if impl in ("fhk", "lua"):
        cc = cross_cut_fhk(tuple(P[:, 0]), tuple(P[:, 1]), tuple(P[:, 2]), tuple(P[:, 3]), P.shape[0], div, tuple(np.unique(P[:, 0])))
    elif impl == "lupa":
        cc = cross_cut_lupa(tuple(P[:, 0]), tuple(P[:, 1]), tuple(P[:, 2]), tuple(P[:, 3]), P.shape[0], div, tuple(np.unique(P[:, 0])))
    else:
        cc = cross_cut_py(P, div)
    return cc(species, breast_height_diameter, height)
