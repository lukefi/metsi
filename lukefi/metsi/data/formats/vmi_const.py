""" Constant data indices of the app """

class VMI12StandIndices:
    """ Class defining the stand indices of VMI12 data """
    lohkomuoto = 1
    section_y = slice(2, 5)
    section_x = slice(5, 8)
    test_area_number = slice(9, 11)
    stand_number = 12
    row_type = 13
    lat = slice(18, 25)
    lon = slice(25, 32)
    osuus9m = slice(36, 38)
    osuus5m = slice(38, 40)
    municipality = slice(45, 48)
    county = slice(48, 50)
    area_ha = slice(50, 59)
    forestry_centre = slice(66, 68)
    kitukunta = slice(68, 71)
    height_above_sea_level = slice(82, 87)
    degree_days = slice(87, 91)
    owner_group = 92
    date = slice(93, 99)
    #TODO: following 3 indices shouldn't need slice notation, but direct index trigggers bug in LueVMI12
    land_category = slice(100, 101)
    land_category_detail = slice(101, 102)
    fra_class = slice(102, 103)
    paatyyppi = 104
    kasvupaikkatunnus = 106
    ojitus_tilanne = 126
    ojitus_tarve = 130
    ojitus_aika = slice(128, 130)
    tax_class = 132
    tax_class_reduction = slice(133, 134)
    puuntuotannon_rajoitus = slice(135, 138)
    puuntuotannon_rajoitus_tarkenne = 138
    suojametsakoodi = 139
    muut_arvot = 140
    naturaaluekoodi = 141
    ahvenanmaan_markkinahakkuualue = 149
    kehitysluokka = 201
    hakkuu_tapa = 262
    hakkuu_aika = 263
    maanmuokkaus = 268
    viljely = 270
    viljely_aika = 271
    muu_toimenpide = 274
    muu_toimenpide_aika = 275
    hakkuuehdotus = 278
    koealan_kasittelyluokka = slice(314, 317)
    pohjapintaala = slice(228, 230)


class VMI12TreeIndices:
    """ Class defining the tree indices of VMI12 data """
    lohkomuoto = 1
    section_y = slice(2, 5)
    section_x = slice(5, 8)
    test_area_number = slice(9, 11)
    tree_type = 11
    stand_number = 12
    tree_number = slice(14, 17)
    species = slice(17, 19)
    diameter = slice(19, 22)
    tree_category = 24
    latvuskerros = 26
    height = slice(36, 40)
    living_branches_height = slice(58, 61)
    measured_height = slice(61, 64)
    d13_age = slice(91, 94)
    age_increase = slice(95, 97)
    total_age = slice(97, 100)


class VMI12StratumIndices:
    """ Class defining the stratum indices of VMI12 data """
    lohkomuoto = 1
    section_y = slice(2, 5)
    section_x = slice(5, 8)
    test_area_number = slice(9, 11)
    stand_number = 12
    stratum_number = slice(15, 17)
    stratum_rank = 19
    species = slice(20, 22)
    origin = 22
    sapling_stems_per_ha = slice(24, 28)
    stems_per_ha = slice(28, 33)
    avg_diameter = slice(36, 38)
    avg_height = slice(39, 42)
    d13_age = slice(44, 47)
    biological_age = slice(47, 49)
    basal_area = slice(50, 52)


class VMI13StandIndices:
    """ Class defining the stand indices of VMI13 data """
    lohkomuoto = 2
    section_y = 3
    section_x = 4
    test_area_number = 5
    stand_number = 6
    date = 9
    osuus9m = 14
    osuus4m = 15
    forestry_centre = 18
    municipality = 17
    kitukunta = 20
    owner_group = 24
    lat = 26
    lon = 27
    height_above_sea_level = 30
    degree_days = 31
    land_category = 42
    land_category_detail = 43
    fra_class = 48
    paatyyppi = 54
    kasvupaikkatunnus = 55
    ojitus_tilanne = 59
    ojitus_aika = 61
    ojitus_tarve = 62
    tax_class = 64
    tax_class_reduction = 65
    hakkuu_tapa = 104
    hakkuu_aika = 105
    maanmuokkaus = 110
    viljely = 112
    viljely_aika = 113
    muu_toimenpide = 115
    muu_toimenpide_aika = 116
    hakkuuehdotus = 117
    puuntuotannon_rajoitus = 127
    puuntuotannon_rajoitus_tarkenne = 128
    suojametsakoodi = 129
    muut_arvot = 130
    naturaaluekoodi = 131
    ahvenanmaan_markkinahakkuualue = 132
    koealan_kasittelyluokka = 133
    kehitysluokka = 72
    pohjapintaala = 88


class VMI13TreeIndices:
    """ Class defining the tree indices of VMI13 data """
    lohkomuoto = 2
    section_y = 3
    section_x = 4
    test_area_number = 5
    stand_number = 6
    tree_number = 7
    tree_type = 12
    species = 13
    diameter = 14
    tree_category = 15
    latvuskerros = 16
    height = 18
    living_branches_height = 26
    measured_height = 27
    d13_age = 46
    age_increase = 48
    total_age = 49


class VMI13StratumIndices:
    """ Class defining the stratum indices of VMI13 data """
    lohkomuoto = 2
    section_y = 3
    section_x = 4
    test_area_number = 5
    stand_number = 6
    stratum_number = 7
    stratum_rank = 11
    species = 12
    origin = 13
    sapling_stems_per_ha = 14
    stems_per_ha = 15
    avg_diameter = 16
    avg_height = 17
    d13_age = 19
    biological_age = 20
    basal_area = 22


vmi12_county_areas = [
    341.144731908512, 333.997181334169, 0.0, 342.095800524934, 344.973457199735, 342.790305010893,
    337.97691292876, 341.680159256802, 344.538163001294, 334.106632294352, 388.636152954809,
    384.104671280277, 387.185442744553, 380.530710444382, 387.55872063968, 391.846213895394,
    455.901059564719, 773.027950310559, 451.83355704698, 791.65080, 10313.25275, 230.82912
]

# Inventointialueiden koealojen pinta-alat(0=Ahve 1=V-Suomi 2=E-Suomi 3=Kai-PP 4=Lappi, 5=Y-Lappi)
# tarkista Ahve ja Y-Lappi
vmi13_county_areas = [343.0, 436.0, 343.0, 456.0, 784.0, 784.0]

# scots pine, norway spruce, silver birch, downy birch, aspen, alder
species_directly_mappable = ['1', '2', '3', '4', '5', '6']
# tervaleppä (??? alder?)
species_other_alder = ['7']
# other deciduous species
species_other_deciduous = ['8', '9', 'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'C1']
# other coniferous species
species_other_coniferous = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
