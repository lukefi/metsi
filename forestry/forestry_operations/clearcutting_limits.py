"""
Clearcuttings are simulated if the treestock's mean age
or mean diameter at breast height exceeds the renewal limit
given in separate files (renewal_ages_southernFI.txt, 
renewal_diameters_southernFI.txt ...).
Values in files are based on Tapio's Best practices for sustainable
forest management in Finland: https://metsanhoidonsuositukset.fi/en. 
There are separate files for different regions(Southern, Central, Northern),
regional tables have columns by dominant species (Scots Pine, 
Norway Spruce, Silver Birch, Downy Birch) and rows by site type 
(OMT, MT, VT, CT). 
"""
from typing import List, Tuple
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.forestry import forestry_utils as futil
from forestry.forestry_operations.thinning_limits import SiteTypeKey, SpeciesKey, site_type_to_key

RENEWAL_DIAMETERS = {
        SiteTypeKey.OMT: {
            SpeciesKey.PINE:26,
            SpeciesKey.SPRUCE:28,
            SpeciesKey.SILVER_BIRCH:23,
            SpeciesKey.DOWNY_BIRCH:23,
        },
        SiteTypeKey.MT: {
            SpeciesKey.PINE:26,
            SpeciesKey.SPRUCE:26,
            SpeciesKey.SILVER_BIRCH:23,
            SpeciesKey.DOWNY_BIRCH:23,
        },
        SiteTypeKey.VT: {
            SpeciesKey.PINE: 25,
            SpeciesKey.SPRUCE: 24,
            SpeciesKey.SILVER_BIRCH:25,
            SpeciesKey.DOWNY_BIRCH:21,
        },
        SiteTypeKey.CT: {
            SpeciesKey.PINE:22,
            SpeciesKey.SPRUCE: 22,
            SpeciesKey.SILVER_BIRCH: 22,
            SpeciesKey.DOWNY_BIRCH:19
        }
    }

RENEWAL_AGES = {
        SiteTypeKey.OMT: {
            SpeciesKey.PINE:70,
            SpeciesKey.SPRUCE:60,
            SpeciesKey.SILVER_BIRCH:60,
            SpeciesKey.DOWNY_BIRCH:50,
        },
        SiteTypeKey.MT: {
            SpeciesKey.PINE:70,
            SpeciesKey.SPRUCE:70,
            SpeciesKey.SILVER_BIRCH:60,
            SpeciesKey.DOWNY_BIRCH:50,
        },
        SiteTypeKey.VT: {
            SpeciesKey.PINE: 80,
            SpeciesKey.SPRUCE: 60,
            SpeciesKey.SILVER_BIRCH:60,
            SpeciesKey.DOWNY_BIRCH:50,
        },
        SiteTypeKey.CT: {
            SpeciesKey.PINE:90,
            SpeciesKey.SPRUCE: 60,
            SpeciesKey.SILVER_BIRCH: 60,
            SpeciesKey.DOWNY_BIRCH:50
        }
    }



def create_clearcutting_limits_table(file_path: str) -> List:
    contents = None
    with open(file_path, "r") as f:
        contents = f.read()
    table = contents.split('\n')
    table = [row.split() for row in table]
    
    if len(table) != 4 or len(table[0]) != 5:
        raise Exception('Clearcutting limits file has unexpected structure. Expected 4 rows and 5 columns, got {} rows and {} columns'.format(len(table), len(table[0])))
    else:
        return table


def get_clearcutting_agelimits_from_parameter_file_contents(
    file_path: str,
    ) -> dict:
    """
    Creates a table from :clearcutting_agelimits
    """
    ages = create_clearcutting_limits_table(file_path)
    RENEWAL_AGES = {
        SiteTypeKey.OMT: {
            SpeciesKey.PINE:int(ages[0][0]),
            SpeciesKey.SPRUCE:int(ages[0][1]),
            SpeciesKey.SILVER_BIRCH:int(ages[0][2]),
            SpeciesKey.DOWNY_BIRCH:int(ages[0][3]),
        },
        SiteTypeKey.MT: {
            SpeciesKey.PINE:int(ages[1][0]),
            SpeciesKey.SPRUCE:int(ages[1][1]),
            SpeciesKey.SILVER_BIRCH:int(ages[1][2]),
            SpeciesKey.DOWNY_BIRCH:int(ages[1][3]),
        },
        SiteTypeKey.VT: {
            SpeciesKey.PINE: int(ages[2][0]),
            SpeciesKey.SPRUCE: int(ages[2][1]),
            SpeciesKey.SILVER_BIRCH:int(ages[2][2]),
            SpeciesKey.DOWNY_BIRCH:int(ages[2][3]),
        },
        SiteTypeKey.CT: {
            SpeciesKey.PINE:int(ages[3][0]),
            SpeciesKey.SPRUCE: int(ages[3][1]),
            SpeciesKey.SILVER_BIRCH: int(ages[3][2]),
            SpeciesKey.DOWNY_BIRCH:int(ages[3][3])
        }
    }
    return RENEWAL_AGES

def get_clearcutting_diameterlimits_from_parameter_file_contents(
    file_path: str,
    ) -> dict:
    """
    Creates a table from :clearcutting_diamterlimits
    """
    diameters = create_clearcutting_limits_table(file_path)
    RENEWAL_DIAMETERS = {
        SiteTypeKey.OMT: {
            SpeciesKey.PINE:float(diameters[0][0]),
            SpeciesKey.SPRUCE:float(diameters[0][1]),
            SpeciesKey.SILVER_BIRCH:float(diameters[0][2]),
            SpeciesKey.DOWNY_BIRCH:float(diameters[0][3]),
        },
        SiteTypeKey.MT: {
            SpeciesKey.PINE:float(diameters[1][0]),
            SpeciesKey.SPRUCE:float(diameters[1][1]),
            SpeciesKey.SILVER_BIRCH:float(diameters[1][2]),
            SpeciesKey.DOWNY_BIRCH:float(diameters[1][3]),
        },
        SiteTypeKey.VT: {
            SpeciesKey.PINE: float(diameters[2][0]),
            SpeciesKey.SPRUCE: float(diameters[2][1]),
            SpeciesKey.SILVER_BIRCH:float(diameters[2][2]),
            SpeciesKey.DOWNY_BIRCH:float(diameters[2][3]),
        },
        SiteTypeKey.CT: {
            SpeciesKey.PINE:float(diameters[3][0]),
            SpeciesKey.SPRUCE: float(diameters[3][1]),
            SpeciesKey.SILVER_BIRCH: float(diameters[3][2]),
            SpeciesKey.DOWNY_BIRCH:float(diameters[3][3])
        }
    }
    return RENEWAL_DIAMETERS



def get_clearcutting_limits(stand: ForestStand, file_path_ages: str = None, file_path_diameters: str = None) -> Tuple[int, float]:
    """ Finds minimum age and and minimum mean diameter for clearcutting
    a stand from parameter files defined in control. yaml. It is user's responsibility to provide it in correct format. 
    Parsing failure will raise an exception. 
    If file not provided in control.yaml, the hardcoded structures will be used."""
    site_type_key = site_type_to_key(stand.site_type_category)
    species_key = species_to_key_clearcut(stand)
    if file_path_ages is not None:
        age_limits = get_clearcutting_agelimits_from_parameter_file_contents(file_path_ages)
        age_limit = age_limits[site_type_key][species_key]
    else:
        age_limit = RENEWAL_AGES[site_type_key][species_key]
    if file_path_diameters is not None:
        diameter_limits = get_clearcutting_diameterlimits_from_parameter_file_contents(file_path_diameters)
        diameter_limit = diameter_limits[site_type_key][species_key]
    else:
        diameter_limit = RENEWAL_DIAMETERS[site_type_key][species_key]
    return (age_limit,diameter_limit)


def species_to_key_clearcut(stand:ForestStand) -> str:
    """ converts tree species to into a key for clearcut lookup table """
    value = futil.solve_dominant_species(stand.reference_trees)
    if value in (TreeSpecies.PINE,):
        return  SpeciesKey.PINE
    elif value in (TreeSpecies.SPRUCE,):
        return SpeciesKey.SPRUCE
    elif value in (TreeSpecies.SILVER_BIRCH,):
        return SpeciesKey.SILVER_BIRCH
    elif value in (TreeSpecies.DOWNY_BIRCH,):
        return SpeciesKey.DOWNY_BIRCH
    elif value in (TreeSpecies.ASPEN, TreeSpecies.GREY_ALDER,
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
        return SpeciesKey.DOWNY_BIRCH
    else:
        raise UserWarning("Unable to spesify tree species value {} as key for the thinning limits lookup table".format(value))
