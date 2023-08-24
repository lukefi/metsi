from lukefi.metsi.data.enums.forest_centre import (
    ForestCentreSiteType,
    ForestCentreOwnerCategory,
    ForestCentreSoilPeatlandCategory,
    ForestCentreSpecies,
    ForestCentreLandUseCategory,
    ForestCentreDrainageCategory, ForestCentreStratumStorey
)
from lukefi.metsi.data.enums.internal import (
    SiteType,
    OwnerCategory,
    SoilPeatlandCategory,
    TreeSpecies,
    LandUseCategory,
    DrainageCategory, Storey
)

_species_map = {
    ForestCentreSpecies.PINE: TreeSpecies.PINE,
    ForestCentreSpecies.SPRUCE: TreeSpecies.SPRUCE,
    ForestCentreSpecies.SILVER_BIRCH: TreeSpecies.SILVER_BIRCH,
    ForestCentreSpecies.DOWNY_BIRCH: TreeSpecies.DOWNY_BIRCH,
    ForestCentreSpecies.ASPEN: TreeSpecies.ASPEN,
    ForestCentreSpecies.GREY_ALDER: TreeSpecies.GREY_ALDER,
    ForestCentreSpecies.COMMON_ALDER: TreeSpecies.COMMON_ALDER,
    ForestCentreSpecies.OTHER_CONIFEROUS: TreeSpecies.OTHER_CONIFEROUS,
    ForestCentreSpecies.OTHER_DECIDUOUS: TreeSpecies.OTHER_DECIDUOUS,
    ForestCentreSpecies.DOUGLAS_FIR: TreeSpecies.DOUGLAS_FIR,
    ForestCentreSpecies.JUNIPER: TreeSpecies.JUNIPER,
    ForestCentreSpecies.SHORE_PINE: TreeSpecies.SHORE_PINE,
    ForestCentreSpecies.EUROPEAN_WHITE_ELM: TreeSpecies.EUROPEAN_WHITE_ELM,
    ForestCentreSpecies.LARCH: TreeSpecies.LARCH,
    ForestCentreSpecies.SMALL_LEAVED_LIME: TreeSpecies.SMALL_LEAVED_LIME,
    ForestCentreSpecies.BLACK_SPRUCE: TreeSpecies.BLACK_SPRUCE,
    ForestCentreSpecies.WILLOW: TreeSpecies.WILLOW,
    ForestCentreSpecies.MOUNTAIN_ASH: TreeSpecies.MOUNTAIN_ASH,
    ForestCentreSpecies.ABIES: TreeSpecies.ABIES,
    ForestCentreSpecies.GOAT_WILLOW: TreeSpecies.GOAT_WILLOW,
    ForestCentreSpecies.COMMON_ASH: TreeSpecies.COMMON_ASH,
    ForestCentreSpecies.KEDAR: TreeSpecies.KEDAR,
    ForestCentreSpecies.SERBIAN_SPRUCE: TreeSpecies.SERBIAN_SPRUCE,
    ForestCentreSpecies.OAK: TreeSpecies.OAK,
    ForestCentreSpecies.BIRD_CHERRY: TreeSpecies.BIRD_CHERRY,
    ForestCentreSpecies.MAPLE: TreeSpecies.MAPLE,
    ForestCentreSpecies.CURLY_BIRCH: TreeSpecies.CURLY_BIRCH,
    ForestCentreSpecies.WYCH_ELM: TreeSpecies.WYCH_ELM,
    ForestCentreSpecies.UNKNOWN_CONIFEROUS: TreeSpecies.UNKNOWN_CONIFEROUS,
    ForestCentreSpecies.UNKNOWN_DECIDUOUS: TreeSpecies.UNKNOWN_DECIDUOUS,
    ForestCentreSpecies.BIRCH: TreeSpecies.SILVER_BIRCH,
    ForestCentreSpecies.ALDER: TreeSpecies.GREY_ALDER,
    ForestCentreSpecies.MIXED: TreeSpecies.OTHER_DECIDUOUS
}


_land_use_map = {
    ForestCentreLandUseCategory.FOREST: LandUseCategory.FOREST,
    ForestCentreLandUseCategory.SCRUB_LAND: LandUseCategory.SCRUB_LAND,
    ForestCentreLandUseCategory.WASTE_LAND: LandUseCategory.WASTE_LAND,
    ForestCentreLandUseCategory.OTHER_FOREST: LandUseCategory.OTHER_FOREST,
    ForestCentreLandUseCategory.AGRICULTURAL: LandUseCategory.AGRICULTURAL,
    ForestCentreLandUseCategory.REAL_ESTATE: LandUseCategory.REAL_ESTATE,
    ForestCentreLandUseCategory.OTHER_LAND: LandUseCategory.OTHER_LAND,
    ForestCentreLandUseCategory.WATER_BODY: LandUseCategory.WATER_BODY
}


_owner_map = {
    ForestCentreOwnerCategory.PRIVATE: OwnerCategory.PRIVATE,
    ForestCentreOwnerCategory.FOREST_INDUSTRY: OwnerCategory.FOREST_INDUSTRY,
    ForestCentreOwnerCategory.STATE: OwnerCategory.OTHER_STATE_AGENCY,
    ForestCentreOwnerCategory.JULKISYHTEISO: OwnerCategory.OTHER_COMMUNITY
}


_soil_peatland_map = {
    ForestCentreSoilPeatlandCategory.MINERAL_SOIL: SoilPeatlandCategory.MINERAL_SOIL,
    ForestCentreSoilPeatlandCategory.SPRUCE_MIRE: SoilPeatlandCategory.SPRUCE_MIRE,
    ForestCentreSoilPeatlandCategory.PINE_MIRE: SoilPeatlandCategory.PINE_MIRE,
    ForestCentreSoilPeatlandCategory.BARREN_TREELESS_MIRE: SoilPeatlandCategory.TREELESS_MIRE,
    ForestCentreSoilPeatlandCategory.RICH_TREELESS_MIRE: SoilPeatlandCategory.TREELESS_MIRE
}


_site_type_map = {
    ForestCentreSiteType.LEHTO: SiteType.VERY_RICH_SITE,
    ForestCentreSiteType.LEHTOMAINEN_KANGAS: SiteType.RICH_SITE,
    ForestCentreSiteType.TUOREKANGAS: SiteType.DAMP_SITE,
    ForestCentreSiteType.KUIVAHKOKANGAS: SiteType.SUB_DRY_SITE,
    ForestCentreSiteType.KUIVAKANGAS: SiteType.DRY_SITE,
    ForestCentreSiteType.KARUKKOKANGAS: SiteType.BARREN_SITE,
    ForestCentreSiteType.KALLIOMAA_TAI_HIETIKKO: SiteType.ROCKY_OR_SANDY_AREA,
    ForestCentreSiteType.LAKIMETSA_TAI_TUNTURI: SiteType.OPEN_MOUNTAINS
}


_drainage_category_map = {
    ForestCentreDrainageCategory.OJITTAMATON_KANGAS: DrainageCategory.UNDRAINED_MINERAL_SOIL,
    ForestCentreDrainageCategory.SOISTUNUT_KANGAS: DrainageCategory.MINERAL_SOIL_TURNED_MIRE,
    ForestCentreDrainageCategory.OJITTETTU_KANGAS: DrainageCategory.DITCHED_MINERAL_SOIL,
    ForestCentreDrainageCategory.LUONNONTILAINEN_SUO: DrainageCategory.UNDRAINED_MIRE,
    ForestCentreDrainageCategory.OJIKKO: DrainageCategory.DITCHED_MIRE,
    ForestCentreDrainageCategory.MUUTTUMA: DrainageCategory.TRANSFORMING_MIRE,
    ForestCentreDrainageCategory.TURVEKANGAS: DrainageCategory.TRANSFORMED_MIRE
}


_storey_map = {
    ForestCentreStratumStorey.DOMINANT: Storey.DOMINANT,
    ForestCentreStratumStorey.UNDER: Storey.UNDER,
    ForestCentreStratumStorey.OVER: Storey.OVER,
    ForestCentreStratumStorey.SPARE: Storey.SPARE,
    ForestCentreStratumStorey.REMOTE: Storey.REMOTE,
    ForestCentreStratumStorey.REMOVAL: Storey.REMOVAL
}

def convert_drainage_category(code: str):
    value = ForestCentreDrainageCategory(code)
    return _drainage_category_map.get(value)


def convert_site_type_category(code: str) -> SiteType:
    value = ForestCentreSiteType(code)
    return _site_type_map.get(value)


def convert_soil_peatland_category(sp_code: str) -> SoilPeatlandCategory:
    value = ForestCentreSoilPeatlandCategory(sp_code)
    return _soil_peatland_map.get(value)


def convert_land_use_category(lu_code: str) -> LandUseCategory:
    fc_category = ForestCentreLandUseCategory(lu_code)
    return _land_use_map.get(fc_category)


def convert_species(species_code: str) -> TreeSpecies:
    """Converts FC species code to internal TreeSpecies code"""
    fc_species = ForestCentreSpecies(species_code)
    return _species_map.get(fc_species)


def convert_owner(owner_code: str) -> OwnerCategory:
    fc_owner = ForestCentreOwnerCategory(owner_code)
    return _owner_map.get(fc_owner)


def convert_storey(storey_code: str) -> Storey:
    fc_storey = ForestCentreStratumStorey(storey_code)
    return _storey_map.get(fc_storey)
