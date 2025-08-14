from typing import Optional
from collections.abc import Sequence
from datetime import datetime as dt
from shapely.geometry import Point
from geopandas import GeoSeries

from lukefi.metsi.data.enums.internal import Storey
from lukefi.metsi.data.formats.util import get_or_default, parse_float, parse_int
from lukefi.metsi.data.formats.vmi_const import vmi12_county_areas
from lukefi.metsi.app.utils import MetsiException


def determine_area_factors(small_tree_sourcevalue: str, big_tree_sourcevalue: str) -> tuple[float, float]:
    """Compute forest stand specific scaling factors for area and reference tree stem count scaling."""
    small = get_or_default(parse_float(small_tree_sourcevalue), 0.0) / 10
    big = get_or_default(parse_float(big_tree_sourcevalue), 0.0) / 10
    return small, big


def determine_artificial_regeneration_year(regeneration: str, regeneration_year: str, year: int) -> Optional[int]:
    if regeneration in ('1', '2', '3', '4'):
        if regeneration_year == '0':
            return year
        if regeneration_year == '1':
            return year - 1
        if regeneration_year == '2':
            return year - 3
        if regeneration_year == '3':
            return year - 8
        if regeneration_year in ('a', 'A'):
            return year - 20
        if regeneration_year in ('b', 'B'):
            return year - 35
    return None


def determine_development_class(dev_class_source: str) -> int:
    if dev_class_source in {'1', '2', '3', '4', '5', '6', '7', '8', '9'}:
        return int(dev_class_source)
    return 0


def determine_natural_renewal(natural_renewal: str) -> bool:
    return natural_renewal.strip() in {'8', '9'}


def determine_clearing_of_reform_sector_year(other_method: str, year_adjustment_class: str, year: int) -> Optional[int]:
    """Determine the year of reform sector clearing when "other method" matches with the correct class in VMI terms"""
    if other_method == '4':
        if year_adjustment_class == "0":
            return year
        if year_adjustment_class == "1":
            return year - 1
        if year_adjustment_class == "2":
            return year - 3
        if year_adjustment_class == "3":
            return year - 8
    return None


def determine_pruning_year(other_method: str, year_adjustment_class: str, year: int) -> Optional[int]:
    """Determine the year of pruning when "other method" matches with the correct class in VMI terms"""
    if other_method == '3':
        if year_adjustment_class == "0":
            return year
        if year_adjustment_class == "1":
            return year - 1
        if year_adjustment_class == "2":
            return year - 3
        if year_adjustment_class == "3":
            return year - 7
    return None


def determine_drainage_year(sourcevalue: str, year: int) -> Optional[int]:
    try:
        value = int(sourcevalue)
        return year - value
    except (TypeError, ValueError):
        return None


def determine_drainage_feasibility(ojitus_tarve: str) -> bool:
    return ojitus_tarve in ('1', '2', '3')


def determine_vmi12_area_ha(lohkomuoto: int, county: int) -> float:
    area_ha = 0.0
    if county < 1 or county >= len(vmi12_county_areas):
        raise IndexError
    if county < 17:
        area_ha = vmi12_county_areas[(county - 1)]
    elif county == 17 and lohkomuoto == 3:
        area_ha = vmi12_county_areas[(county - 1)]
    elif county == 17 and lohkomuoto == 4:
        area_ha = vmi12_county_areas[county]
    elif county == 18:
        area_ha = vmi12_county_areas[18]
    elif county == 19 and lohkomuoto == 4:
        area_ha = vmi12_county_areas[19]
    elif county == 19 and lohkomuoto == 5:
        area_ha = vmi12_county_areas[20]
    elif county == 21:
        area_ha = vmi12_county_areas[21]
    return round(area_ha, 4)


def _solve_vmi13_county_areas(county: int, lohkomuoto: int, lohkotarkenne: int) -> float:
    if county == 1 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 345.73918
    if county == 2 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 338.0386443
    if county == 4 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 342.975010960105
    if county == 5 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 342.747528
    if county == 6 and lohkotarkenne == 0:
        if lohkomuoto == 1:
            return 413.08125
        if lohkomuoto == 2:
            return 347.828958275767
    if county == 7 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 342.438585979628
    if county == 8 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 349.917881811205
    if county == 9 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 350.8972332
    if county == 10 and lohkomuoto == 2 and lohkotarkenne == 0:
        return 340.4779333
    if county == 11:
        if lohkomuoto == 1:
            return 436.521343
        if lohkomuoto == 2:
            return 330.3735632
    if county == 12 and lohkotarkenne == 0:
        if lohkomuoto == 1:
            return 433.4836506
        if lohkomuoto == 2:
            return 351.5358362
    if county == 13 and lohkomuoto == 1 and lohkotarkenne == 0:
        return 435.9383152
    if county == 14 and lohkomuoto == 1 and lohkotarkenne == 0:
        return 429.5909091
    if county == 15 and lohkomuoto == 1 and lohkotarkenne == 0:
        return 434.9541716
    if county == 16 and lohkomuoto == 1 and lohkotarkenne == 0:
        return 435.0433276
    if county == 17 and lohkotarkenne == 0:
        if lohkomuoto == 3:
            return 457.7258227
        if lohkomuoto == 4:
            return 747.6246246
    if county == 18 and lohkomuoto == 3 and lohkotarkenne == 0:
        return 455.8440533
    if county == 19:
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
    if county == 21 and lohkomuoto == 0 and lohkotarkenne == 0:
        return 164.2650475

    raise MetsiException(f"Unable to solve vmi13 country area weight for values: \
                        county {county}, lohkomuoto {lohkomuoto} and lohkotarkenne {lohkotarkenne}")


def determine_vmi13_area_ha(county: int, lohkomuoto: int, lohkotarkenne: int) -> float:
    if county < 0 and lohkomuoto < 0 or lohkotarkenne < 0:
        raise IndexError
    return _solve_vmi13_county_areas(county, lohkomuoto, lohkotarkenne)


def determine_soil_surface_preparation_year(sourcevalue: str, year: int) -> Optional[int]:
    """Determine the year of soil surface preparation from given VMI source classes and the year of data set."""
    if sourcevalue == '0':
        return year
    if sourcevalue == '1':
        return year - 1
    if sourcevalue == '2':
        return year - 3
    if sourcevalue == '3':
        return year - 8
    if sourcevalue in {'A', 'a'}:
        return year - 20
    return None


def determine_forest_maintenance_details(cutting_type_class: str, sourcevalue: str, year: int):
    """
    Return a triplet of (young_stand_tending_year, cutting_year, cutting_method). VMI source data is exclusive
    between cutting and tending, i.e. the codes are overloaded into the same year class variable. RST target format
    allows separate value for both tending and cutting years, but this is impossible in source data.
    """
    operation_year = determine_forest_maintenance_year(sourcevalue, year)
    method = determine_forest_maintenance_method(cutting_type_class, operation_year)

    if cutting_type_class in ('1', '2'):
        return operation_year, None, None
    if method == 0:
        # This case is necessary. Operations over 10 years old are listed as type 0, or no operation in VMI data.
        # The actual year is still recorded, but we don't seem to want it in RST target. This is based on original
        # implementation of this application.
        return None, None, None
    return None, operation_year, method


def determine_forest_maintenance_year(sourcevalue: str, year: int) -> Optional[int]:
    """Determine the year of last operation from given VMI source classes and the year of data set."""
    if sourcevalue in ('0', '1', '2', '3', '4', '5'):
        return year - int(sourcevalue)
    if sourcevalue == '6':
        return year - 7
    if sourcevalue in {'A', 'a'}:
        return year - 20
    if sourcevalue in {'B', 'b'}:
        return year - 40
    return None


def determine_forest_maintenance_method(sourcevalue: str, cutting_year: Optional[int]) -> int:
    """Map VMI cutting method to RST cutting method if cutting year exists"""
    if cutting_year is not None and cutting_year > 0:
        if sourcevalue == '0':
            return 0
        if sourcevalue == '4':
            return 1
        if sourcevalue == '7':
            return 2
        if sourcevalue == '3':
            return 3
        if sourcevalue == '6':
            return 4
        if sourcevalue == '8':
            return 5
        if sourcevalue == '9':
            return 6
    return 0


def convert_vmi12_geolocation(lat_source: str, lon_source: str) -> tuple[float, float]:
    """
    Convert VMI12 coordinates in EPSG:2393 to EPSG:3067. Source values are in meter precision, return values are
    likewise rounded to meter precision.
    :param lat_source: EPSG:2393 latitude
    :param lon_source: EPSG:2393 longitude
    :return: lat, lon tuple in EPSG:3067
    """
    point = GeoSeries([Point(float(lon_source), float(lat_source))], crs='EPSG:2393')
    point = point.to_crs(3067)
    return round(point.centroid.y[0]), round(point.centroid.x[0])


def convert_vmi12_approximate_geolocation(lat_source: str, lon_source: str) -> tuple[float, float]:
    """
    Convert VMI12 coordinates in EPSG:2393 to YKJ/KKJ3 with band 3 prefix removed.

    :param lat_source: source string of the latitude value
    :param lon_source: source string of the llongitude value

    :return (lat,lon): latitude,longitude pair
    """
    lat = float(lat_source)
    lon = float(lon_source) - 3000000
    return lat, lon


def determine_vmi12_dominant_storey_age(ds_bh_age: str, ds_age_increase: str) -> float:
    """ Dominant storey age is composed of dominant storey breast height age and age increase for vmi12. """
    a = get_or_default(parse_float(ds_bh_age), 0.0)
    b = get_or_default(parse_float(ds_age_increase), 0.0)
    return a + b


def determine_vmi13_dominant_storey_age(ds_age) -> float:
    """ Dominant storey mean age for vmi13 """
    return get_or_default(parse_float(ds_age), 0.0)


def parse_vmi12_date(date_string: str) -> dt:
    """Generate a datetime entry out of VMI12 date source format ddmmyy"""
    return dt.strptime(date_string, '%d%m%y')


def parse_vmi13_date(date_string: str) -> dt:
    """Generate a datetime entry out of VMI13 date source format yyyymmdd"""
    return dt.strptime(date_string, '%Y%m%d')


def transform_vmi12_height_above_sea_level(sourcevalue: str) -> float | None:
    """
    Transform given VMI12 number value string from desimeters to meters.
    Returning float, or None on error.
    """
    try:
        return float(sourcevalue) / 10.0
    except ValueError:
        return None


def transform_vmi13_height_above_sea_level(sourcevalue: str) -> float | None:
    """Return given number value string as float, or None on error"""
    try:
        return float(sourcevalue)
    except ValueError:
        return None


def transform_vmi_degree_days(sourcevalue: str) -> float | None:
    """Return given number value string as float or None on error"""
    try:
        return float(sourcevalue)
    except ValueError:
        return None


def determine_tax_class_reduction(sourcevalue: str) -> int:
    """
    Map and return number valued source string as integer for values 0 to 4. Otherwise 0.
    """
    if sourcevalue == '0':
        return 0
    if sourcevalue == '1':
        return 1
    if sourcevalue == '2':
        return 2
    if sourcevalue == '3':
        return 3
    if sourcevalue == '4':
        return 4
    return 0


def determine_tax_class(sourcevalue: str) -> int:
    """
    Map and return number valued source string as int for values [0,4] => [1,5]. Otherwise 0.
    """
    # TODO: string - int type ambiguity in maaluokka. Could not have matched int.
    # Arto Haara comment please, is it needed?
    # if (maaluokka == 2):
    #     veroluokka = 6.0
    # elif (maaluokka == 3):
    #     veroluokka = 7.0

    if sourcevalue == '0':
        return 1
    if sourcevalue == '1':
        return 2
    if sourcevalue == '2':
        return 3
    if sourcevalue == '3':
        return 4
    if sourcevalue == '4':
        return 5
    return 0


# TODO: default case undefined. Problem? Original implementation raises NameError from undefined in else case
def determine_owner_group(sourcevalue: str) -> int:
    """Map and transform integer valued source string as integer or raise on unknown values"""
    if sourcevalue in ['0', '1']:
        return 0
    if sourcevalue in ['2', '3']:
        return 1
    if sourcevalue in ['4', '5']:
        return 2
    if sourcevalue in ['7', '8']:
        return 3
    if sourcevalue in ['6', '9']:
        return 4
    raise MetsiException('Unknown source value for owner_group')


def parse_forestry_centre(forestry_centre: str) -> int:
    try:
        return int(forestry_centre)
    except (ValueError, TypeError):
        return 10


def determine_forest_management_category(land_category: int, forestry_centre: int, muuttujat: Sequence,
                                         owner_group: int, indices: dict,
                                         is_vmi12: bool = True) -> int:
    """Determine forest management category  for given conditions."""

    fmc = 1
    other_values = muuttujat[indices["muut_arvot"]]

    # TODO: VMI13 full data shows regression with land category comparison. Probably a bug
    if is_vmi12:
        fmc = determine_fmc_by_land_category(fmc, land_category)
    fmc = determine_fmc_by_production_limitations(fmc, other_values, owner_group,
                                                  muuttujat[indices["puuntuotannon_rajoitus"]],
                                                  muuttujat[indices["puuntuotannon_rajoitus_tarkenne"]],
                                                  muuttujat[indices["suojametsakoodi"]])
    # fmc = determine_fmc_by_natura_area(fmc, muuttujat[indices.naturaaluekoodi])
    fmc = determine_fmc_by_aland_centre(fmc, muuttujat[indices["ahvenanmaan_markkinahakkuualue"]], forestry_centre,
                                        other_values)
    forest_management_category_override = determine_fmc_by_test_area_handling_class(
        muuttujat[indices["koealan_kasittelyluokka"]])

    # VMI-raj korvataan tiukemmalla MH-rajoituksella
    fmc = max(fmc, forest_management_category_override)

    return fmc


def determine_fmc_by_land_category(default: int, land_category: int) -> int:
    if land_category == 1:
        return 1
    if land_category == 2:
        return 3
    if land_category == 3:
        return 6
    return default


def determine_fmc_by_production_limitations(default: int, other_values: str, owner_group: int,
                                            production_limitation: str, production_limitation_detail: str,
                                            protection_forest_code: str) -> int:
    if production_limitation == '0':
        return 1
    if production_limitation in \
            ('101', '102', '103', '104', '105', '108'):
        return 7
    if production_limitation in ('201', '205', '206', '207') and \
            production_limitation_detail in ('1', '2'):
        return 7
    if production_limitation == '301':
        return 7
    if production_limitation in ('302', '303', '304', '305', '306', '307', '308', '309', '310') and \
            production_limitation_detail in ('1', '2'):
        return 7
    if production_limitation in ('401', '402', '403', '404', '408', '409'):
        return 7
    if production_limitation in ('405', '406', '407') and \
            production_limitation_detail in ('1', '2'):
        return 7
    if production_limitation in ('501', '502', '503', '504') and \
            production_limitation_detail in ('1', '2'):
        return 7
    if production_limitation in ('107', '109') and \
            production_limitation_detail in ('3', '4'):
        return 2
    if production_limitation in ('201', '205', '206', '207') and \
            production_limitation_detail in ('3', '4'):
        return 2
    if production_limitation in ('202', '203') and \
            production_limitation_detail in ('1', '2', '3', '4'):
        return 2
    if production_limitation in ('302', '303', '304', '305', '306', '307', '308', '309', '310') and \
            production_limitation_detail in ('3', '4'):
        return 2
    if production_limitation in ('405', '406', '407') and \
            production_limitation_detail in ('3', '4'):
        return 2
    if production_limitation in ('501', '502', '503', '504') and \
            production_limitation_detail in ('3', '4'):
        return 2
    if other_values in ('1', '2', '3', '4', '5', '6'):
        return 2
    # Lisäksi suojametsät metsähallituksen mailla;
    if protection_forest_code == '1' and owner_group == 4:
        return 2
    return default


def determine_fmc_by_natura_area(default: int, natura_area_code: str) -> int:
    # Natura-alueet: luonto-kohteet (2) ja molemmat (3) pois puuntuotannosta;
    # Tarkista onko minaan vuonna voimassa
    if natura_area_code in ('2', '3'):
        return 1  # * lintu-kohde=1;
    return default


def determine_fmc_by_aland_centre(default: int, aland_area_code: str, forestry_centre: int,
                                  other_values: str) -> int:
    # * Ahvenanmaa;
    if forestry_centre == 21 and (aland_area_code != '1' or other_values == '2'):
        return 7
    return default


def determine_fmc_by_test_area_handling_class(test_area_handling_class: str) -> int:
    # Metsähallituksen rajoitukset;
    fmc = 1  # MH, ei rajoituksia
    if test_area_handling_class != '.':
        if test_area_handling_class == '1':
            fmc = 1
        if test_area_handling_class == '2':
            fmc = 2
        if test_area_handling_class in ('3.1', '3.2'):
            fmc = 7
    return fmc


def determine_municipality(municipality_code: str, kitukunta: str) -> Optional[int]:
    """
    Return by order of precedence: valid municipality code, valid kitukunta code, or None.
    """
    retval = parse_int(vmi_codevalue(municipality_code))
    if retval is None:
        retval = parse_int(vmi_codevalue(kitukunta))
    return retval


def vmi_codevalue(source: str) -> Optional[str]:
    value = source.strip()
    if value in ('', '.'):
        return None
    return value


def determine_tree_age_values(chest_height_age_source: str, age_increase_source: str,
                              total_age_source: str) -> tuple[int | None, int | None]:
    chest_height_age = parse_int(chest_height_age_source)
    age_increase = parse_int(age_increase_source)
    total_age = parse_int(total_age_source)

    if total_age:
        computed_age = total_age
    elif age_increase and chest_height_age:
        computed_age = chest_height_age + age_increase
    elif chest_height_age:
        computed_age = chest_height_age + 9
    else:
        computed_age = None

    return None if chest_height_age == 0 else chest_height_age, computed_age


def determine_tree_management_category(sourcevalue: str) -> int:
    return 2 if sourcevalue.lower() in ('b', 'c', 'd', 'e', 'f', 'g') else 1


def transform_tree_diameter(source: str) -> float:
    return get_or_default(parse_float(source), 0.0) / 10.0


def determine_tree_height(height_sourcevalue: str, conversion_factor: float = 10.0) -> Optional[float]:
    """
    return tree height in meters as transformed from VMI dm values or computed with the Näslund height model
    if VMI value is not available.

    :param height_sourcevalue: integer string assumed to represent decimeters
    :param diameter:
    :param species:
    :return:
    """
    h = get_or_default(parse_float(vmi_codevalue(height_sourcevalue)), 0.0)
    return h / conversion_factor if h > 0 else None


def determine_stems_per_ha(diameter: float | None, is_vmi12: bool) -> float:
    if diameter is None:
        raise MetsiException("Missing diameter")
    medium_diameter_vmi_constant = 5.64 if is_vmi12 else 4.0
    if 0.0 < diameter < 4.5:
        return round(1.5 / (3.141592653589793 * ((diameter / 2) / 100.0) ** 2), 0)
    if 4.5 <= diameter < 9.5:
        return round(10000.0 / (3.141592653589793 * (medium_diameter_vmi_constant ** 2)), 3)
    if diameter >= 9.5:
        return round(10000.0 / (3.141592653589793 * (9.0 ** 2)), 3)
    return 1.0


def generate_stand_identifier(row: Sequence, indices: dict) -> str:
    return row[indices["lohkomuoto"]] + "-" + \
        row[indices["section_y"]] + "-" + \
        row[indices["section_x"]] + "-" + \
        row[indices["test_area_number"]] + "-" + \
        row[indices["stand_number"]]


def generate_tree_identifier(row: Sequence, indices: dict) -> str:
    return row[indices["lohkomuoto"]] + "-" + \
        row[indices["section_y"]] + "-" + \
        row[indices["section_x"]] + "-" + \
        row[indices["test_area_number"]] + "-" + \
        row[indices["stand_number"]] + "-" + \
        row[indices["tree_number"]] + "-" + \
        "tree"


def generate_stratum_identifier(row: Sequence, indices: dict) -> str:
    return row[indices["lohkomuoto"]] + "-" + \
        row[indices["section_y"]] + "-" + \
        row[indices["section_x"]] + "-" + \
        row[indices["test_area_number"]] + "-" + \
        row[indices["stand_number"]] + "-" + \
        row[indices["stratum_number"]] + "-" + \
        "stratum"


def determine_stratum_tree_height(source_height: str) -> Optional[float]:
    maybe_height = parse_float(source_height)
    if maybe_height is not None and maybe_height > 0:
        return round(maybe_height / 10, 2)
    return None


def determine_stratum_origin(source_origin: str) -> int:
    # return value explanations:
    # 0 is natural
    # 1 is seeded
    # 2 is planted
    if source_origin == "3":
        return 2
    if source_origin == "4":
        return 1
    return 0


def determine_stratum_age_values(biological_age_source: str,
                                 breast_height_age_source: str,
                                 height: Optional[float]) -> tuple[float, float]:
    """ Determinates biological age and breast height age for vmi source data.

        param: biological_age_source: Stratum biological age or age increase value as vmi source value.
        param: breast_height_age_source: Stratum breast height age as vmi source value
        param: height (optional): Stratum height value

        return: Biological and breast height age as a tuple of whole number floats
    """
    computational_age = get_or_default(parse_float(biological_age_source), 0.0)
    breast_height_age = get_or_default(parse_float(breast_height_age_source), 0.0)
    if height is None:
        height = 0.0

    if computational_age == 0 and breast_height_age > 0:
        computational_age = breast_height_age + 9
    elif computational_age == 0 and breast_height_age == 0 and height > 0:
        if height > 1.3:
            breast_height_age = 1.4 * height
            computational_age = breast_height_age + 8
            breast_height_age = round(breast_height_age, 0)
            computational_age = round(computational_age, 0)
        else:
            # sapling biological age
            computational_age = 1.4 * height
            computational_age = round(computational_age, 0)
    elif computational_age > 0 and breast_height_age == 0 and height > 1.3:
        breast_height_age = 1.4 * height
        computational_age = breast_height_age + computational_age
        breast_height_age = round(breast_height_age, 0)
        computational_age = round(computational_age, 0)
    elif computational_age > 0:
        computational_age = computational_age + breast_height_age
    else:
        computational_age = 0.0

    return (computational_age, breast_height_age)


def determine_storey_for_stratum(source: str) -> Optional[Storey]:
    """Determinates storey for stratum based on vmi source value 'ositteen asema'."""
    parsed = parse_int(source)
    if parsed in [0, 1]:
        return Storey.DOMINANT
    if parsed in [2, 3, 4]:
        return Storey.OVER
    if parsed in [5, 6, 7, 9]:
        return Storey.UNDER
    if parsed in [8]:
        return Storey.INDETERMINATE
    return None


def determine_storey_for_tree(source: str) -> Optional[Storey]:
    """Determinates storey for vmi tree based on vmi source value 'latvuskerros'."""
    parsed = parse_int(source)
    if parsed in [2, 3, 4]:
        return Storey.DOMINANT
    if parsed in [5]:
        return Storey.UNDER
    if parsed in [6, 7]:
        return Storey.OVER
    return None


def determine_tree_type(source: str) -> Optional[str]:
    if source in (' ', '.', ''):
        return None
    return source
