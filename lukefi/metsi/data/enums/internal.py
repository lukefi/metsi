from enum import IntEnum


class TreeSpecies(IntEnum):
    """This list is formed by combining VMI and Forest centre species 
    and listing all the distinct ones. UNKNOWN (38) is not part of either list, 
    but can be assigned to in case the source data species is unexpected."""
    PINE = 1
    SPRUCE = 2
    SILVER_BIRCH = 3
    DOWNY_BIRCH = 4
    ASPEN = 5
    GREY_ALDER = 6
    COMMON_ALDER = 7
    OTHER_CONIFEROUS = 8
    OTHER_DECIDUOUS = 9
    DOUGLAS_FIR = 10
    JUNIPER = 11
    SHORE_PINE = 12
    EUROPEAN_WHITE_ELM = 13
    LARCH = 14
    SMALL_LEAVED_LIME = 15
    BLACK_SPRUCE = 16
    WILLOW = 17
    MOUNTAIN_ASH = 18
    ABIES = 19
    GOAT_WILLOW = 20
    COMMON_ASH = 21
    KEDAR = 22
    SERBIAN_SPRUCE = 23
    OAK = 24
    BIRD_CHERRY = 25
    MAPLE = 26
    CURLY_BIRCH = 27
    WYCH_ELM = 28
    UNKNOWN_CONIFEROUS = 29
    UNKNOWN_DECIDUOUS = 30
    OTHER_PINE = 31
    OTHER_SPRUCE = 32
    THUJA = 33
    YEW = 34
    BAY_WILLOW = 35
    POPLAR = 36
    HAZEL = 37
    UNKNOWN = 38


class LandUseCategory(IntEnum):
    FOREST = 1
    SCRUB_LAND = 2
    WASTE_LAND = 3
    OTHER_FOREST = 4
    AGRICULTURAL = 5
    BUILT_LAND = 6
    ROAD = 7
    ENERGY_TRANSMISSION_LINE = 8
    FRESHWATER = 9
    SEA = 10
    REAL_ESTATE = 11
    OTHER_LAND = 12
    WATER_BODY = 13


class OwnerCategory(IntEnum):
    UNKNOWN = 0
    PRIVATE = 1
    FOREST_INDUSTRY = 2
    OTHER_ENTERPRISE = 3
    METSAHALLITUS = 4
    OTHER_STATE_AGENCY = 5
    FOREST_COOP = 6
    MUNICIPALITY = 7
    CONGREGATION = 8
    OTHER_COMMUNITY = 9
    UNDIVIDED = 10


class SoilPeatlandCategory(IntEnum):
    MINERAL_SOIL = 1 # kangas
    SPRUCE_MIRE = 2 # korpi
    PINE_MIRE = 3 # räme
    TREELESS_MIRE = 4 # avosuo. Conversion to MELA's Neva or Letto is made with siteType


class SiteType(IntEnum):
    VERY_RICH_SITE = 1
    RICH_SITE = 2
    DAMP_SITE = 3
    SUB_DRY_SITE = 4
    DRY_SITE = 5
    BARREN_SITE = 6
    ROCKY_OR_SANDY_AREA = 7
    OPEN_MOUNTAINS = 8
    TUNTURIKOIVIKKO = 9
    LAKIMETSA_TAI_TUNTURIHAVUMETSA = 10


class DrainageCategory(IntEnum):
    UNDRAINED_MINERAL_SOIL_OR_MIRE = 1
    UNDRAINED_MINERAL_SOIL = 2
    MINERAL_SOIL_TURNED_MIRE = 3
    DITCHED_MINERAL_SOIL = 4
    UNDRAINED_MIRE = 5
    DITCHED_MIRE = 6
    TRANSFORMING_MIRE = 7
    TRANSFORMED_MIRE = 8
