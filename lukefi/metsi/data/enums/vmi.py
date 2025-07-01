from enum import Enum


class VmiSpecies(Enum):
    PINE = "1"
    SPRUCE = "2"
    SILVER_BIRCH = "3"
    DOWNY_BIRCH = "4"
    ASPEN = "5"
    GREY_ALDER = "6"
    COMMON_ALDER = "7"
    MOUNTAIN_ASH = "8"
    GOAT_WILLOW = "9"
    OTHER_CONIFEROUS = "A0"
    SHORE_PINE = "A1"
    KEDAR = "A2"
    OTHER_PINE = "A3"
    LARCH = "A4"
    ABIES = "A5"
    OTHER_SPRUCE = "A6"
    THUJA = "A7"
    JUNIPER = "A8"
    YEW = "A9"
    OTHER_DECIDUOUS = "B0"
    BAY_WILLOW = "B1"
    EUROPEAN_WHITE_ELM = "B2"
    WYCH_ELM = "B3"
    SMALL_LEAVED_LIME = "B4"
    POPLAR = "B5"
    COMMON_ASH = "B6"
    OAK = "B7"
    BIRD_CHERRY = "B8"
    MAPLE = "B9"
    HAZEL = "C1"
    UNKNOWN = None

    @classmethod
    def _missing_(cls, value):
        if value == "0":
            return cls.UNKNOWN
        return None


class VmiLandUseCategory(Enum):
    FOREST = '1'
    SCRUB_LAND = '2'
    WASTE_LAND = '3'
    OTHER_FOREST = '4'
    AGRICULTURAL = '5'
    BUILT_LAND = '6'
    ROAD = '7'
    ENERGY_TRANSMISSION_LINE = '8'
    FRESHWATER = 'A'
    SEA = 'B'
    OBSOLETE = 'C'


class VmiOwnerCategory(Enum):
    UNKNOWN = "0"
    # private
    PRIVATE = "1"
    # enterprise
    FOREST_INDUSTRY_ENTERPRISE = "2"
    OTHER_ENTERPRISE = "3"
    # state forest
    METSAHALLITUS = "4"
    OTHER_STATE_AGENCY = "5"
    # communities
    FOREST_COOP = "6"  # = yhteismetsä
    MUNICIPALITY = "7"
    CONGREGATION = "8"
    OTHER_COMMUNITY = "9"
    # jakamaton
    UNDIVIDED = "A"  # = jakamaton kuolinpesä


class VmiSoilPeatlandCategory(Enum):
    MINERAL_SOIL = '1'
    SPRUCE_MIRE = '2'
    PINE_MIRE = '3'
    TREELESS_MIRE = '4'


class VmiSiteType(Enum):
    LEHTO = '1'
    LEHTOMAINEN_KANGAS = '2'
    TUOREKANGAS = '3'
    KUIVAHKOKANGAS = '4'
    KUIVAKANGAS = '5'
    KARUKKOKANGAS = '6'
    KALLIOMAA_TAI_HIETIKKO = '7'
    LAKIMETSA_TAI_TUNTURIHAVUMETSA = '8'
    TUNTURIKOIVIKKO = 'T'
    AVOTUNTURI = 'A'


class VmiDrainageCategory(Enum):
    OJITTAMATON_KANGAS_TAI_SUO = '0'
    OJITETTU_KANGAS = '1'
    OJIKKO = '2'
    MUUTTUMA = '3'
    TURVEKANGAS = '4'


class VmiStratumRank(Enum):
    UNGROWABLE_SAPLINGS = '0'
    DOMINANT = '1'
    OVER_1 = '2'
    OVER_2 = '3'
    OVER_3 = '4'
    UNDER_1 = '5'
    UNDER_2 = '6'
    UNDER_3 = '7'
    UNDER_4 = '9'
    REMOVAL = '8'


class VmiTreeStorey(Enum):
    DOMINANT_MAIN = '2'
    DOMINANT_MIDDLE = '3'
    DOMINANT_LOWER = '4'
    UNDER = '5'
    OVER_MAIN = '6'
    OVER_OTHER = '7'
    DOMINANT_SPARE_1 = 'B'
    DOMINANT_SPARE_2 = 'C'
    DOMINANT_SPARE_3 = 'D'
    UNDER_SPARE_1 = 'E'
    OVER_SPARE_1 = 'F'
    OVER_SPARE_2 = 'G'
