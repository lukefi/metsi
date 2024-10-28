""" Constant data indices used in building the output file """


class RSTStandIndices:
    """ RST stand indices """
    man_unit = 0
    year = 1
    area = 2
    areaweight = 3
    north = 4
    east = 5
    id_number = 6
    mpy = 7
    dd = 8
    owner = 9
    land_use = 10
    soil = 11
    site = 12
    reduction = 13
    tax_site = 14
    drain_class = 15
    feas_drain = 16
    no_value1 = 17
    drainyear = 18
    fertil = 19
    soil_prepa = 20
    nat_regen = 21
    clean_year = 22
    dev_class = 23
    art_regen = 24
    tending = 25
    pruning = 26
    cut_year = 27
    for_centre = 28
    mana_cate = 29
    cut_method = 30
    municipality = 31
    system1 = 32
    system2 = 33


class RSTTreeIndices:
    """ RST tree indices """
    stems_per_ha = 0  # taulussa 3
    species = 1  # taulussa 4
    diameter = 2  # taulussa 5
    height = 3  # taulussa 6
    d13_age = 4  # taulussa 7
    biological_age = 5  # taulussa 8
    log_reduction = 6  # taulussa 9
    pruning = 7  # taulussa 10
    age10 = 8  # taulussa 11
    origin = 9  # taulussa 12
    id_tree = 10  # taulussa 13
    direction = 11  # taulussa 14
    distance = 12  # taulussa 15
    height_difference = 13  # taulussa 16
    living_branch = 14  # taulussa 17
    man_category = 15  # taulussa 18
    system3 = 16  # taulussa 19


class MSBInitialDataRecordConst:
    stand_record_length = 34
    tree_record_length = 17
    physical_record_header_length = 2
    logical_record_header_length = 2
    logical_record_metadata_length = 1
    logical_subrecord_metadata_length = 2
    logical_record_type = 1
