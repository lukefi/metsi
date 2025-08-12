import enum

# puulaji
class Species(enum.IntEnum):
    PINE         = 1     # mänty
    SPRUCE       = 2     # kuusi
    SILVER_BIRCH = 3     # hieskoivu
    DOWNY_BIRCH  = 4     # rauduskoivu
    ASPEN        = 5     # haapa
    GRAY_ALDER   = 6     # harmaaleppä
    BLACK_ALDER  = 7     # tervaleppä
    CONIFEROUS   = 8     # havupuu
    DECIDUOUS    = 9     # lehtipuu

# jakso
class Storie(enum.IntEnum):
    NONE         = 0     # jaksoton (onko tämä edes järkevä/mahdollinen?)
    LOWER        = 1     # alempi jakso
    UPPER        = 2     # ylempi jakso
    OVER         = 3     # ylispuusto?
    RETENTION    = 4     # säästöpuut

# syntytapa / perustustapa / uudistustapa, miksi tätä nyt haluaakaan kutsua.
class Origin(enum.IntEnum):
    NATURAL      = 1     # luontainen
    SEEDED       = 2     # kylvetty
    PLANTED      = 3     # istutettu

# maanmuokkaustapa
class SoilPrep(enum.IntEnum):
    NONE           = 0   # ei muokkausta
    SCALPING       = 1   # laikutus
    HARROWING      = 2   # äestys
    PATCH_MOUNDING = 3   # laikkumätästys
    DITCH_MOUNDING = 4   # ojitusmätästys
    INVERTING      = 5   # kääntömätästys
    OTHER          = 6   # "muokattu"

# taimityyppi
class SaplingType(enum.IntEnum):
    CULTIVATED   = 1   # kehityskelpoinen viljelty
    NATURAL      = 2   # kehityskelpoinen luontaisesti syntynyt
    INFEASIBLE   = 3   # kehityskelvoton

# maaluokka (mal)
class LandUseCategoryVMI(enum.IntEnum):
    FOREST       = 1
    SCRUB        = 2
    WASTE        = 3
    FOREST_OTHER = 4
    AGRICULTURAL = 5
    BUILTUP      = 6
    ROAD         = 7
    LAKE         = 8
    SEA          = 9

# metsätyyppi (mty)
class SiteTypeVMI(enum.IntEnum):
    OMaT         = 1
    OMT          = 2
    MT           = 3
    VT           = 4
    CT           = 5
    ClT          = 6
    ROCKY        = 7
    MOUNTAIN     = 8

# alaryhmä (alr)
class SoilCategoryVMI(enum.IntEnum):
    MINERAL      = 1
    PEAT_SPRUCE  = 2     # korpi
    PEAT_PINE    = 3     # räme
    PEAT_BARREN  = 4     # neva
    PEAT_RICH    = 5     # letto

# veroluokan vähennys
class TaxClassReduction(enum.IntEnum):
    NONE        = 0
    STONY       = 1
    WET         = 2
    MOSS        = 3  # kunttaisuus
    LOCATION    = 4

# veroluokan tarkennus
class TaxClass(enum.IntEnum):
    IA          = 1
    IB          = 2
    II          = 3
    III         = 4
    IV          = 5
    SCRUB       = 6
    WASTE       = 7

# ojitustilanne
class DitchStatus(enum.IntEnum):
    MSOIL_UNDITCHED = 0   # ojittamaton kangas
    MINERALSOIL     = 1   # ojitettu kangas
    PEAT_UNDITCHED  = 2   # ojittamaton suo
    PEAT_UNAFFECTED = 3   # ojikko (suo, jolla ojitus ei vaikuta kasvuun)
    PEAT_AFFECTED   = 4   # muuttuma (suo, jolla ojituksella on selvä vaikutus)
    PEAT_TKG        = 5   # turvekangas

# ojien kunto
class DitchCondition(enum.IntEnum):
    BAD         = 0
    GOOD        = 1

# lannoitustyyppi
class FertilizerType(enum.IntEnum):
    AMMONIUM_SULFATE = 1    # ammoniumsulfaatti
    UREA             = 2    # urea
    CALCIUM_NITRATE  = 3    # salpietari
    PK               = 4    # P-K (fosfori+kalium)
    NPK              = 5    # N-P-K (typpi+fosfori+kalium)
    ASH              = 6    # tuhka

# fosforilannoitus
class AddedPhosphorus(enum.IntEnum):
    NOT_ADDED = 0
    ADDED     = 1

# turvekangastyyppi
class TkgTypeVasanderLaine(enum.IntEnum):
    RHTKG1 = 51
    RHTKG2 = 52
    MTKG1  = 53
    MTKG2  = 54
    PTKG1  = 55
    PTKG2  = 56
    VATKG1 = 57
    VATKG2 = 58
    JATK   = 59

# suotyyppi
class PeatTypeSINKA(enum.IntEnum):
    VLK   = 1
    KoLK  = 2
    LhK   = 3
    VLR   = 4
    RLR   = 5
    VL    = 6
    RL    = 7
    RhSK  = 8
    RhK   = 9
    RhSR  = 10
    RhSN  = 11
    RhRiN = 12
    VSK   = 13
    MK    = 14
    KgK   = 15
    VSR   = 16
    VRN   = 17
    MKR   = 18
    PK    = 19
    PsK   = 20
    PKgK  = 21
    PsR   = 22
    KgR   = 23
    PKR   = 24
    TSR   = 25
    VkR   = 26
    LkR   = 27
    LkKN  = 28
