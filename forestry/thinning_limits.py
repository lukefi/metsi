"""
The module is basicly a utility file for thinning operations that are basal area based.

Thinning limits lookup table is used for solving lower (y0) and upper (y1) bound
of basal area thinnings.
"""
from functools import cache, lru_cache
from typing import Dict, List, Tuple
from enum import Enum
from collections.abc import KeysView
from bisect import bisect
from forestdatamodel.model import ForestStand
from forestdatamodel.enums.internal import TreeSpecies
from forestryfunctions import forestry_utils as futil

class CountyKey(Enum):
    EASTERN_FINLAND = 'eastern_finland'
    SOUTHERN_FINLAND = 'southern_finland'


class SiteTypeKey(Enum):
    OMT = 'OMT'
    MT = 'MT'
    VT = 'VT'
    CT = 'CT'


class SoilPeatlandKey(Enum):
    MINERAL_SOIL = 'mineral_soil'
    PEATLAND = 'peatland'


class SpeciesKey(Enum):
    PINE = 'pine'
    SPRUCE = 'spruce'
    SILVER_BIRCH = 'silver_birch_and_other_deciduous'
    DOWNY_BIRCH = 'downy_birch'


THINNING_LIMITS = {
    CountyKey.EASTERN_FINLAND :{
        SoilPeatlandKey.MINERAL_SOIL: {
            SiteTypeKey.OMT: {
                SpeciesKey.PINE:  {
                    # dominant_height: (basal_area_0=y0, basal_area_1=y1)
                    10: (15.3, 24.0),
                    12: (15.3, 24.0),
                    14: (17.6, 24.0),
                    16: (19.0, 26.1),
                    18: (19.6, 27.4),
                    20: (19.9, 28.1),
                    22: (19.9, 28.0),
                    24: (19.9, 28.0),
                    26: (19.9, 28.0)
                },
                SpeciesKey.SPRUCE:  {
                    10: (15.2, 24.0),
                    12: (15.2, 24.0),
                    14: (18.4, 27.0),
                    16: (20.9, 30.0),
                    18: (22.8, 32.0),
                    20: (23.9, 33.0),
                    22: (23.9, 33.0),
                    24: (23.9, 33.0),
                    26: (23.9, 33.0)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (8.5, 16.0),
                    12: (8.5, 16.0),
                    14: (10.9, 16.9),
                    16: (12.7, 18.9),
                    18: (14.1, 19.8),
                    20: (15.0, 20.7),
                    22: (15.0, 20.7),
                    24: (15.0, 20.7),
                    26: (15.0, 20.7)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
            SiteTypeKey.MT: {
                SpeciesKey.PINE:  {
                    10: (15.3, 24.0),
                    12: (15.3, 24.0),
                    14: (17.6, 24.0),
                    16: (19.0, 26.1),
                    18: (19.6, 27.4),
                    20: (19.9, 28.1),
                    22: (19.9, 28.0),
                    24: (19.9, 28.0),
                    26: (19.9, 28.0)
                },
                SpeciesKey.SPRUCE:  {
                    10: (15.3, 24.0),
                    12: (15.3, 24.0),
                    14: (17.6, 24.0),
                    16: (19.0, 26.1),
                    18: (19.6, 27.4),
                    20: (19.9, 28.1),
                    22: (19.9, 28.0),
                    24: (19.9, 28.0),
                    26: (19.9, 28.0)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (8.5, 16.0),
                    12: (8.5, 16.0),
                    14: (10.9, 16.9),
                    16: (12.7, 18.9),
                    18: (14.1, 19.8),
                    20: (15.0, 20.7),
                    22: (15.0, 20.7),
                    24: (15.0, 20.7),
                    26: (15.0, 20.7)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
            SiteTypeKey.VT: {
                SpeciesKey.PINE:  {
                    10: (14.2, 20.0),
                    12: (14.2, 20.0),
                    14: (15.9, 21.9),
                    16: (17.0, 24.9),
                    18: (17.6, 25.8),
                    20: (17.9, 25.7),
                    22: (18.1, 25.7),
                    24: (18.1, 25.7),
                    26: (18.1, 25.7)
                },
                SpeciesKey.SPRUCE:  {
                    10: (15.3, 24.0),
                    12: (15.3, 24.0),
                    14: (17.6, 24.0),
                    16: (19.0, 26.1),
                    18: (19.6, 27.4),
                    20: (19.9, 28.1),
                    22: (19.9, 28.0),
                    24: (19.9, 28.0),
                    26: (19.9, 28.0)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
            SiteTypeKey.CT: {
                SpeciesKey.PINE:  {
                    10: (12.0, 18.0),
                    12: (12.0, 18.0),
                    14: (14.1, 18.9),
                    16: (15.5, 21.9),
                    18: (16.1, 22.8),
                    20: (16.1, 22.7),
                    22: (16.1, 22.7),
                    24: (16.1, 22.7),
                    26: (16.1, 22.7)
                },
                SpeciesKey.SPRUCE:  {
                    10: (12.0, 18.0),
                    12: (12.0, 18.0),
                    14: (14.1, 18.9),
                    16: (15.5, 21.9),
                    18: (16.1, 22.8),
                    20: (16.1, 22.7),
                    22: (16.1, 22.7),
                    24: (16.1, 22.7),
                    26: (16.1, 22.7)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
        },
        SoilPeatlandKey.PEATLAND: {
            SiteTypeKey.OMT: {
                SpeciesKey.PINE: {
                    10: (15.3, 21.0),
                    12: (15.3, 21.0),
                    14: (17.6, 24.5),
                    16: (19.0, 26.7),
                    18: (19.6, 27.7),
                    20: (19.9, 28.3),
                    22: (19.9, 28.4),
                    24: (19.9, 28.4),
                    26: (19.9, 28.4)
                },
                SpeciesKey.SPRUCE: {
                    10: (15.2, 24.0),
                    12: (15.2, 24.0),
                    14: (18.4, 27.0),
                    16: (20.9, 30.0),
                    18: (22.8, 32.0),
                    20: (23.9, 33.0),
                    22: (23.9, 33.0),
                    24: (23.9, 33.0),
                    26: (23.9, 33.0)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (8.5, 16.0),
                    12: (8.5, 16.0),
                    14: (10.9, 16.9),
                    16: (12.7, 18.9),
                    18: (15.0, 19.8),
                    20: (15.0, 20.7),
                    22: (15.0, 20.7),
                    24: (15.0, 20.7),
                    26: (15.0, 20.7)
                },
                SpeciesKey.DOWNY_BIRCH: {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
            SiteTypeKey.MT: {
                SpeciesKey.PINE:  {
                    10: (15.3, 21.0),
                    12: (15.3, 21.0),
                    14: (17.6, 24.5),
                    16: (19.0, 26.7),
                    18: (19.6, 27.7),
                    20: (19.9, 28.3),
                    22: (19.9, 28.4),
                    24: (19.9, 28.4),
                    26: (19.9, 28.4)
                },
                SpeciesKey.SPRUCE:  {
                    10: (15.3, 24.0),
                    12: (15.3, 24.0),
                    14: (17.6, 24.0),
                    16: (19.0, 26.1),
                    18: (19.6, 27.4),
                    20: (19.9, 28.1),
                    22: (19.9, 28.0),
                    24: (19.9, 28.0),
                    26: (19.9, 28.0)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (8.5, 16.0),
                    12: (8.5, 16.0),
                    14: (10.9, 16.9),
                    16: (12.7, 18.9),
                    18: (14.1, 19.8),
                    20: (15.0, 20.7),
                    22: (15.0, 20.7),
                    24: (15.0, 20.7),
                    26: (15.0, 20.7)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
            SiteTypeKey.VT: {
                SpeciesKey.PINE:  {
                    10: (13.2, 19.5),
                    12: (13.2, 19.5),
                    14: (16.3, 23.2),
                    16: (17.3, 25.2),
                    18: (17.8, 26.1),
                    20: (18.0, 26.4),
                    22: (18.0, 26.4),
                    24: (18.0, 26.4),
                    26: (18.0, 26.4)
                },
                SpeciesKey.SPRUCE:  {
                    10: (15.3, 24.0),
                    12: (15.3, 24.0),
                    14: (17.6, 24.0),
                    16: (19.0, 26.1),
                    18: (19.6, 27.4),
                    20: (19.9, 28.1),
                    22: (19.9, 28.0),
                    24: (19.9, 28.0),
                    26: (19.9, 28.0)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            },
            SiteTypeKey.CT: {
                SpeciesKey.PINE:  {
                    10: (12.8, 17.5),
                    12: (12.8, 17.5),
                    14: (15.3, 21.2),
                    16: (16.1, 23.1),
                    18: (16.5, 23.8),
                    20: (16.5, 23.8),
                    22: (16.5, 23.8),
                    24: (16.5, 23.8),
                    26: (16.5, 23.8)
                },
                SpeciesKey.SPRUCE:  {
                    10: (12.8, 17.5),
                    12: (12.8, 17.5),
                    14: (15.3, 21.2),
                    16: (16.1, 23.1),
                    18: (16.5, 23.8),
                    20: (16.5, 23.8),
                    22: (16.5, 23.8),
                    24: (16.5, 23.8),
                    26: (16.5, 23.8)
                },
                SpeciesKey.SILVER_BIRCH: {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                },
                SpeciesKey.DOWNY_BIRCH:   {
                    10: (10.4, 14.0),
                    12: (10.4, 14.0),
                    14: (11.7, 16.0),
                    16: (12.7, 17.4),
                    18: (13.4, 18.9),
                    20: (13.4, 18.9),
                    22: (13.4, 18.9),
                    24: (13.4, 18.9),
                    26: (13.4, 18.9)
                }
            }
        }
    }
}


def site_type_to_key(value: int) -> str:
    """  converts site type of stand into a key for thinning limist lookup table

    site_type variable explanations:
    (1) very rich sites (OMaT in South Finland)
    (2) rich sites (OMT in South Finland)
    (3) damp sites (MT in South Finland)
    (4) sub-dry sites (VT in South Finland)
    (5) dry sites (CT in South Finland)
    (6) barren sites (ClT in South Finland)
    (7) rocky or sandy areas
    (8) open mountains

    """
    if value in (1,2):
        return SiteTypeKey.OMT
    elif value in (3,):
        return SiteTypeKey.MT
    elif value in (4,):
        return SiteTypeKey.VT
    elif value in (5, 6, 7, 8):
        return SiteTypeKey.CT
    elif value < 1 or value > 8:
        return SiteTypeKey.MT
    else:
        raise UserWarning('Unable to spesify site type value {} as key for the thinning limits lookup table'.format(value))


def soil_peatland_category_to_key(value: int) -> str:
    """ converts soil and peatland category of stand into a key for thinning limist lookup table """
    if value in (1,):
        return SoilPeatlandKey.MINERAL_SOIL
    elif value in (2, 3, 4, 5):
        return SoilPeatlandKey.PEATLAND
    else:
        raise UserWarning('Unable to spesify soil and peatland value {} as key for the thinning limits lookup table'.format(value))


def species_to_key(value: int) -> str:
    """ converts tree species to into a key for thinning limits lookup table """
    if value in (TreeSpecies.PINE,):
        return  SpeciesKey.PINE
    elif value in (TreeSpecies.SPRUCE,):
        return SpeciesKey.SPRUCE
    elif value in (TreeSpecies.SILVER_BIRCH, TreeSpecies.ASPEN, TreeSpecies.GREY_ALDER,
        TreeSpecies.OTHER_CONIFEROUS, TreeSpecies.DOUGLAS_FIR, TreeSpecies.JUNIPER,
        TreeSpecies.OTHER_DECIDUOUS, TreeSpecies.SHORE_PINE, TreeSpecies.EUROPEAN_WHITE_ELM,
        TreeSpecies.LARCH, TreeSpecies.SMALL_LEAVED_LIME, TreeSpecies.BLACK_SPRUCE,
        TreeSpecies.WILLOW, TreeSpecies.MOUNTAIN_ASH, TreeSpecies.ABIES,
        TreeSpecies.GOAT_WILLOW, TreeSpecies.COMMON_ASH, TreeSpecies.KEDAR,
        TreeSpecies.SERBIAN_SPRUCE, TreeSpecies.OAK, TreeSpecies.BIRD_CHERRY,
        TreeSpecies.MAPLE, TreeSpecies.CURLY_BIRCH, TreeSpecies.WYCH_ELM,
        TreeSpecies.THUJA, TreeSpecies.YEW, TreeSpecies.BAY_WILLOW, TreeSpecies.POPLAR, TreeSpecies.HAZEL,
        TreeSpecies.OTHER_PINE, TreeSpecies.OTHER_SPRUCE,
        TreeSpecies.UNKNOWN_CONIFEROUS, TreeSpecies.UNKNOWN_DECIDUOUS, TreeSpecies.UNKNOWN):
        return SpeciesKey.SILVER_BIRCH
    elif value in (TreeSpecies.DOWNY_BIRCH,):
        return SpeciesKey.DOWNY_BIRCH
    else:
        raise UserWarning("Unable to spesify tree species value {} as key for the thinning limits lookup table".format(value))


def solve_hdom_key(hdom_x: int, hdoms: KeysView[int]) -> int:
    """ solves dominant height key for stand dominant height for thinning limit lookup table """
    hdoms = list(hdoms)
    i = bisect(hdoms, hdom_x)
    key_idx = min(i, len(hdoms)-1)
    return hdoms[key_idx]


LIMITS_SLICE_LOOKUP = {
    CountyKey.EASTERN_FINLAND :{
        "before_thinning":{
            SoilPeatlandKey.MINERAL_SOIL: {
                SiteTypeKey.OMT: slice(0,4),
                SiteTypeKey.MT: slice(4,8),
                SiteTypeKey.VT: slice(8,12),
                SiteTypeKey.CT: slice(12,16),
            },
            SoilPeatlandKey.PEATLAND: {
                SiteTypeKey.OMT: slice(16,20),
                SiteTypeKey.MT: slice(20,24),
                SiteTypeKey.VT: slice(24,28),
                SiteTypeKey.CT: slice(28,32)
            }
        },
        "after_thinning":{
                SoilPeatlandKey.MINERAL_SOIL: {
                    SiteTypeKey.OMT: slice(32,36),
                    SiteTypeKey.MT: slice(36,40),
                    SiteTypeKey.VT: slice(40,44),
                    SiteTypeKey.CT: slice(44,48),
            },
                SoilPeatlandKey.PEATLAND: {
                    SiteTypeKey.OMT: slice(48,52),
                    SiteTypeKey.MT: slice(52,56),
                    SiteTypeKey.VT: slice(56,60),
                    SiteTypeKey.CT: slice(60,64)
            }
        }
    }
}

@cache
def create_thinning_limits_table(input_data: str) -> List:
    # read thinning_limits into a list of lists
    table = input_data.split('\n')
    table = [row.split() for row in table]

    # this function is based on the structure in data/parameter_files/Thin.txt.
    # for now, to catch a file with a differing structure, raise an error if the row and column numbers do not match.
    if len(table) != 64 or len(table[0]) != 9:
        raise Exception('Thinning limits file has unexpected structure. Expected 64 rows and 9 columns, got {} rows and {} columns'.format(len(table), len(table[0])))
    else:
        return table

@lru_cache
def get_thinning_limits_from_parameter_file_contents(
    thinning_limits: str, 
    county: CountyKey, 
    sp_category: SoilPeatlandKey, 
    site_type: SiteTypeKey, 
    species: SpeciesKey
    ) -> Dict[int, Tuple]:
    """
    Creates a table from :thinning_limits: and uses it to return a dict that contains tuples of lower and upper limits for each height bracket 
    for the given stand parameters (:county:, :sp_category:, :site_type:, :species:).
    """
    limits_table = create_thinning_limits_table(thinning_limits)
    upper_limits_slice = LIMITS_SLICE_LOOKUP[county]["before_thinning"][sp_category][site_type]
    lower_limits_slice = LIMITS_SLICE_LOOKUP[county]["after_thinning"][sp_category][site_type]
    upper_limits = limits_table[upper_limits_slice]
    lower_limits = limits_table[lower_limits_slice]

    if species == SpeciesKey.PINE:
        upper_limits_for_species = upper_limits[0]
        lower_limits_for_species = lower_limits[0]

    elif species == SpeciesKey.SPRUCE:
        upper_limits_for_species = upper_limits[1]
        lower_limits_for_species = lower_limits[1]

    elif species == SpeciesKey.SILVER_BIRCH:
        upper_limits_for_species = upper_limits[2]
        lower_limits_for_species = lower_limits[2]

    elif species == SpeciesKey.DOWNY_BIRCH:
        upper_limits_for_species = upper_limits[3]
        lower_limits_for_species = lower_limits[3]
    
    limit_brackets = [10, 12, 14, 16, 18, 20, 22, 24, 26]
    limits_for_species = {limit_brackets[i]: (float(lower_limits_for_species[i]), float(upper_limits_for_species[i])) for i in range(len(limit_brackets))}

    return limits_for_species


def resolve_thinning_bounds(stand: ForestStand, thinning_limits: str = None) -> Tuple[float, float]:
    """ Resolves lower and upper bound for thinning. Values are in meters (m).
    :thinning_limits: thinning limits from a file parameter defined in control. yaml. It is user's responsibility to provide it in correct format. 
    Parsing failure will raise an exception. 
    If file not provided in control.yaml, the hardcoded THINNING_LIMITS structure will be used."""
    county_key = CountyKey.EASTERN_FINLAND
    sp_category_key = soil_peatland_category_to_key(stand.soil_peatland_category)
    site_type_key = site_type_to_key(stand.site_type_category)
    sdom = futil.solve_dominant_species(stand)
    species_key = species_to_key(sdom)
    hdom = futil.solve_dominant_height_c_largest(stand)

    if thinning_limits is not None:
        spe_limits = get_thinning_limits_from_parameter_file_contents(
            thinning_limits,
            county_key,
            sp_category_key,
            site_type_key,
            species_key
        )
    else:
        spe_limits = THINNING_LIMITS[county_key][sp_category_key][site_type_key][species_key]

    hdom_key = solve_hdom_key(hdom, spe_limits.keys())
    return spe_limits[hdom_key]

# ---- first thinning stem count residue and util functions----

FIRST_THINNING_RESIDUE_STEMS = {
    SiteTypeKey.OMT: {
        SpeciesKey.PINE: 1250.0,
        SpeciesKey.SPRUCE: 1000.0,
        SpeciesKey.SILVER_BIRCH: 750.0,
        SpeciesKey.DOWNY_BIRCH: 950
    },
    SiteTypeKey.MT: {
        SpeciesKey.PINE: 1100,
        SpeciesKey.SPRUCE: 1000,
        SpeciesKey.SILVER_BIRCH: 750,
        SpeciesKey.DOWNY_BIRCH: 950
    },
    SiteTypeKey.VT: {
        SpeciesKey.PINE: 1000,
        SpeciesKey.SPRUCE: 1000,
        SpeciesKey.SILVER_BIRCH: 750,
        SpeciesKey.DOWNY_BIRCH: 950
    },
    SiteTypeKey.CT: {
        SpeciesKey.PINE: 1000,
        SpeciesKey.SPRUCE: 1000,
        SpeciesKey.SILVER_BIRCH: 750,
        SpeciesKey.DOWNY_BIRCH: 950
    }
}


def resolve_first_thinning_residue(stand: ForestStand) -> float:
    """ Resolves stem count residue for first thinning operation. Values are stems per hectare. """
    sdom = futil.solve_dominant_species(stand)
    st_key = site_type_to_key(stand.site_type_category)
    spe_key = species_to_key(sdom)
    lower_limit = FIRST_THINNING_RESIDUE_STEMS[st_key][spe_key]
    return lower_limit
