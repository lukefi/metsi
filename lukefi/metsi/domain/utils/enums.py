from enum import Enum, IntEnum


class SiteTypeKey(Enum):
    OMT = 'OMT'
    MT = 'MT'
    VT = 'VT'
    CT = 'CT'


class SoilPreparationKey(IntEnum):
    NONE = 0
    SCALPING = 1
    HARROWING = 2
    PATCH_MOUNDING = 3
    DITCH_MOUNDING = 4
    INVERTING = 5
    OTHER = 6


class RegenerationKey(IntEnum):
    NATURAL = 1
    SEEDED = 2
    PLANTED = 3
