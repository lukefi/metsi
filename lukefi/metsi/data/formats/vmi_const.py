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
    vallitsevanjakson_d13ika = slice(247,250)
    vallitsevanjakson_ikalisays = slice(250,252)
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
    tuhon_ilmiasu = slice(82,84)
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
    lohkotarkenne = 7
    date = 9
    osuus9m = 14
    osuus4m = 15
    county = 17
    forestry_centre = 18
    municipality = 19
    kitukunta = 20
    owner_group = 24
    lat = 26
    lon = 27
    height_above_sea_level = 30
    degree_days = 31
    land_category = 40
    land_category_detail = 41
    fra_class = 46
    paatyyppi = 52
    kasvupaikkatunnus = 53
    ojitus_tilanne = 57
    ojitus_aika = 59
    ojitus_tarve = 60
    tax_class = 62
    tax_class_reduction = 63
    kehitysluokka = 70
    pohjapintaala = 86
    vallitsevanjaksonika = 95
    hakkuu_tapa = 102
    hakkuu_aika = 103
    maanmuokkaus = 108
    viljely = 110
    viljely_aika = 111
    muu_toimenpide = 113
    muu_toimenpide_aika = 114
    hakkuuehdotus = 115
    puuntuotannon_rajoitus = 125
    puuntuotannon_rajoitus_tarkenne = 126
    suojametsakoodi = 127
    muut_arvot = 128
    naturaaluekoodi = 129
    ahvenanmaan_markkinahakkuualue = 130
    koealan_kasittelyluokka = 131


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
    tree_category = 16
    latvuskerros = 17
    height = 19
    living_branches_height = 27
    measured_height = 28
    tuhon_ilmiasu = 38
    d13_age = 47
    age_increase = 49
    total_age = 50


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
    basal_area = 23


vmi12_county_areas = [
    341.144731908512, 333.997181334169, 0.0, 342.095800524934, 344.973457199735, 342.790305010893,
    337.97691292876, 341.680159256802, 344.538163001294, 334.106632294352, 388.636152954809,
    384.104671280277, 387.185442744553, 380.530710444382, 387.55872063968, 391.846213895394,
    455.901059564719, 773.027950310559, 451.83355704698, 791.65080, 10313.25275, 230.82912
]

def vmi13_county_areas(county: int, lohkomuoto: int, lohkotarkenne: int) -> float:
    if county == 1 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 345.73918
    elif county == 2 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 338.0386443
    elif county == 4 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 342.975010960105
    elif county == 5 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 342.747528
    elif county == 6 and lohkotarkenne == 0:
        if lohkomuoto == 1:
            return 413.08125
        if lohkomuoto == 2:
            return 347.828958275767
    elif county == 7 and lohkomuoto == 2 and lohkotarkenne == 0:
            return 342.438585979628
    elif county == 8 and lohkomuoto == 2 and lohkotarkenne == 0:
            return 349.917881811205
    elif county == 9 and lohkomuoto == 2 and lohkotarkenne == 0:
            return 350.8972332
    elif county == 10 and lohkomuoto == 2 and lohkotarkenne == 0:
            return 340.4779333
    elif county == 11:
        if lohkomuoto == 1:
            return 436.521343
        if lohkomuoto == 2:
            return 330.3735632
    elif county == 12 and lohkotarkenne == 0:
        if lohkomuoto == 1:
            return 433.4836506
        if lohkomuoto == 2:
            return 351.5358362
    elif county == 13 and lohkomuoto == 1 and lohkotarkenne == 0:
            return 435.9383152
    elif county == 14 and lohkomuoto == 1 and lohkotarkenne == 0:
            return 429.5909091
    elif county == 15 and lohkomuoto == 1 and lohkotarkenne == 0:
            return 434.9541716
    elif county == 16 and lohkomuoto == 1 and lohkotarkenne == 0:
            return 435.0433276
    elif county == 17 and lohkotarkenne == 0:
        if lohkomuoto == 3:
            return 457.7258227
        if lohkomuoto == 4: 
            return 747.6246246
    elif county == 18 and lohkomuoto == 3 and lohkotarkenne == 0:
            return 455.8440533
    elif county == 19:
        if lohkomuoto == 4:
            if lohkotarkenne == 0:
                return 786.978534
        if lohkomuoto == 5:
            if lohkotarkenne == 0:
                return 1357.608776
            if lohkotarkenne == 1:
                return 1176.023409
            if lohkotarkenne == 2:
                return 1355.455959
            if lohkotarkenne == 3:
                return 1999.800742
            if lohkotarkenne == 4:
                return 10756.11645
    elif county == 21 and lohkomuoto == 0 and lohkotarkenne == 0:
        return 164.2650475
    else:
        raise Exception("Unable to solve vmi13 country area weight for values: \
                        county {}, lohkomuoto {} and lohkotarkenne {}"
                        .format(county, lohkomuoto, lohkotarkenne))            









    
    

# scots pine, norway spruce, silver birch, downy birch, aspen, alder
species_directly_mappable = ['1', '2', '3', '4', '5', '6']
# tervaleppä (??? alder?)
species_other_alder = ['7']
# other deciduous species
species_other_deciduous = ['8', '9', 'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'C1']
# other coniferous species
species_other_coniferous = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
