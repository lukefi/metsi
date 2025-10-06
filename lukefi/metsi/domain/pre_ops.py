import traceback
from typing import Any
from lukefi.metsi.data.model import ReferenceTree
from lukefi.metsi.data.enums.internal import LandUseCategory
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.domain.utils.filter import applyfilter
from lukefi.metsi.forestry.forestry_utils import find_matching_storey_stratum_for_tree
from lukefi.metsi.forestry.preprocessing import tree_generation, pre_util
from lukefi.metsi.forestry.preprocessing.coordinate_conversion import convert_location_to_ykj, CRS
from lukefi.metsi.forestry.preprocessing.age_supplementing import supplement_age_for_reference_trees
from lukefi.metsi.forestry.preprocessing.naslund import naslund_height
from lukefi.metsi.forestry.preprocessing.tree_generation_validation import create_stratum_tree_comparison_set, \
    debug_output_row_from_comparison_set, debug_output_header_row
from lukefi.metsi.data.vectorize import vectorize
from lukefi.metsi.app.utils import MetsiException


def preproc_filter(stands: StandList, **operation_params) -> StandList:
    named = operation_params.get("named", {})
    for k, v in operation_params.items():
        if k != "named":
            stands = applyfilter(stands, k, v, named)
    return stands


def compute_location_metadata(stands: StandList, **operation_params) -> StandList:
    """
    This operation sets in-place the location based metadata properties for each given ForestStand, where missing.
    These properties are: height above sea level, temperature sum, sea effect, lake effect, monthly temperature and
    monthly rainfall
    """

    # Lazy import of optional MetsiGrow functions.
    from lukefi.metsi.forestry.naturalprocess.MetsiGrow.metsi_grow.lasum import ilmanor  # pylint: disable=import-outside-toplevel
    from lukefi.metsi.forestry.naturalprocess.MetsiGrow.metsi_grow.coord import etrs_tm35_to_ykj as conv  # pylint: disable=import-outside-toplevel
    from lukefi.metsi.forestry.naturalprocess.MetsiGrow.metsi_grow.kor import xkor  # pylint: disable=import-outside-toplevel

    _ = operation_params

    for stand in stands:

        if stand.geo_location is None:
            raise MetsiException(f"Stand {stand.identifier} has no geolocation data")
        if stand.geo_location[0] is None or stand.geo_location[1] is None:
            raise MetsiException(f"Stand {stand.identifier} has incomplete geolocation data: {stand.geo_location}")

        if stand.geo_location[3] == 'EPSG:3067':
            lat, lon = conv(stand.geo_location[0] / 1000, stand.geo_location[1] / 1000)
        elif stand.geo_location[3] == 'EPSG:2393':
            lat, lon = (stand.geo_location[0] / 1000, stand.geo_location[1] / 1000)
        else:
            raise MetsiException(f"Unsupported CRS {stand.geo_location[3]} for stand {stand.identifier}")

        if stand.geo_location[2] is None:
            xkor_value = xkor(lat, lon)
            stand.geo_location = (
                stand.geo_location[0],
                stand.geo_location[1],
                xkor_value,
                stand.geo_location[3])
        else:
            xkor_value = stand.geo_location[2]

        wi = ilmanor(lon, lat, xkor_value)

        if stand.degree_days is None:
            stand.degree_days = wi.dd
        if stand.sea_effect is None:
            stand.sea_effect = wi.sea
        if stand.lake_effect is None:
            stand.lake_effect = wi.lake
        if stand.monthly_temperatures is None:
            stand.monthly_temperatures = wi.temp
        if stand.monthly_rainfall is None:
            stand.monthly_rainfall = wi.rain

    return stands


def generate_reference_trees(stands: StandList, **operation_params) -> StandList:
    """ Operation function that generates (N * stratum) reference trees for each stand """
    debug = operation_params.get('debug', False)
    debug_output_rows = []
    debug_strata_rows = []
    debug_tree_rows = []
    stratum_association_diameter_threshold = operation_params.get('stratum_association_diameter_threshold', 2.5)
    for i, stand in enumerate(stands):
        print(f"\rGenerating trees for stand {stand.identifier}    {i}/{len(stands)}", end="")
        stand_trees = sorted(stand.reference_trees_pre_vec, key=lambda tree: tree.identifier if
                             tree.identifier is not None else "")
        for tree in stand_trees:
            stratum = find_matching_storey_stratum_for_tree(
                tree, stand.tree_strata_pre_vec, stratum_association_diameter_threshold)
            if stratum is None:
                continue
            if stratum.__dict__.get('_trees') is not None:
                getattr(stratum, "_trees").append(tree)
            else:
                setattr(stratum, "_trees", [tree])
            if debug:
                debug_tree_rows.append([
                    stratum.identifier,
                    tree.breast_height_diameter or 'NA',
                    tree.measured_height or 'NA',
                    tree.stems_per_ha or 'NA'
                ])
        stand.tree_strata_pre_vec.sort(key=lambda stratum: stratum.identifier if stratum.identifier is not None else "")
        new_trees: list[ReferenceTree] = []
        for stratum in stand.tree_strata_pre_vec:
            stratum_trees: list[ReferenceTree] = []
            try:
                stratum_trees = tree_generation.reference_trees_from_tree_stratum(stratum, **operation_params)
            except Exception as e:
                print(
                    f"\nError generating trees for stratum {stratum.identifier} with diameter {stratum.mean_diameter}, "
                    f"height {stratum.mean_height}, basal_area {stratum.basal_area}")
                print()
                if debug:
                    traceback.print_exc()
                    continue
                raise e
            stand_tree_count = len(new_trees)
            for i, tree in enumerate(stratum_trees):
                tree.identifier = f"{stand.identifier}-{stand_tree_count + i + 1}-tree"
                new_trees.append(tree)
            validation_set = create_stratum_tree_comparison_set(stratum, stratum_trees)

            if debug:
                debug_strata_rows.append([
                    stratum.identifier,
                    stratum.mean_diameter,
                    stratum.mean_height,
                    stand.basal_area,
                    stratum.basal_area,
                    stratum.species.value if stratum.species is not None else None,
                    stand.degree_days
                ])
                debug_output_rows.append(debug_output_row_from_comparison_set(stratum, validation_set))
        stand.reference_trees_pre_vec = new_trees
    print()
    if debug:
        import csv  # pylint: disable=import-outside-toplevel
        with open('debug_generated_tree_results.csv', 'w', newline='\n', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(debug_output_header_row())
            writer.writerows(debug_output_rows)
        if len(debug_strata_rows) > 1:
            with open('r_strata.dat', 'w', newline='\n', encoding="utf-8") as stratum_file:
                writer = csv.writer(stratum_file, delimiter=' ')
                writer.writerow(["stratum", "DGM", "HGM", "G", "Gos", "spe", "DDY"])
                writer.writerows(debug_strata_rows)
        if len(debug_tree_rows) > 1:
            with open('r_trees.dat', 'w', newline='\n', encoding="utf-8") as tree_file:
                writer = csv.writer(tree_file, delimiter=' ')
                writer.writerow(["stratum", "lpm", "height", "lkm"])
                writer.writerows(debug_tree_rows)
    return stands


def supplement_missing_tree_heights(stands: StandList, **operation_params) -> StandList:
    """ Fill in missing (None or nonpositive) tree heights from Näslund height curve """
    _ = operation_params
    for stand in stands:
        for tree in stand.reference_trees_pre_vec:
            if (tree.height or 0) <= 0:
                tree.height = naslund_height(tree.breast_height_diameter, tree.species)
    return stands


def supplement_missing_tree_ages(stands: StandList, **operation_params) -> StandList:
    """ Attempt to fill in missing (None or nonpositive) tree ages using strata ages or other reference tree ages"""
    _ = operation_params
    for stand in stands:
        supplement_age_for_reference_trees(stand.reference_trees_pre_vec, stand.tree_strata_pre_vec)
    return stands


def supplement_missing_stratum_diameters(stands: StandList, **operation_params) -> StandList:
    """ Attempt to fill in missing (None) stratum mean diameters using mean height """
    _ = operation_params
    for stand in stands:
        for stratum in stand.tree_strata_pre_vec:
            if stratum.mean_diameter is None:
                if stratum.has_height_over_130_cm() and stand.land_use_category == LandUseCategory.SCRUB_LAND:
                    pre_util.supplement_mean_diameter(stratum)
                elif stratum.sapling_stratum and stratum.mean_height:
                    pre_util.supplement_mean_diameter(stratum)
    return stands


def generate_sapling_trees_from_sapling_strata(stands: StandList, **operation_params) -> StandList:
    """ Create sapling reference trees from sapling strata """
    _ = operation_params
    for stand in stands:
        for stratum in stand.tree_strata_pre_vec:
            if stratum.sapling_stratum:
                sapling = stratum.to_sapling_reference_tree()
                stand.reference_trees_pre_vec.append(sapling)
                sapling.stand = stand
                tree_number = len(stand.reference_trees_pre_vec) + 1
                sapling.identifier = f"{stand.identifier}-{tree_number}-tree"
    return stands


def scale_area_weight(stands: StandList, **operation_params):
    """ Scales area weight of a stand.

        Especially necessary for VMI tree generation cases.
        Should be used as precesing operation before the generation of reference trees.
    """
    _ = operation_params
    for stand in stands:
        stand.area_weight = stand.area_weight * stand.area_weight_factors[1]
    return stands


def convert_coordinates(stands: StandList, **operation_params: dict[str, Any]) -> StandList:
    """ Preprocessing operation for converting the current coordinate system to target system

    :target_system (optional): Spesified target system. Default is EPSG:2393
    """
    defaults = CRS.EPSG_2393.value
    target_system = operation_params.get('target_system', defaults[0])
    if target_system in defaults:
        for s in stands:
            if s.geo_location is not None:
                latitude, longitude, height, crs = s.geo_location
                if latitude is not None and longitude is not None:
                    s.geo_location = convert_location_to_ykj(latitude, longitude, height, crs)
    else:
        raise MetsiException("Check definition of operation params.\n"
                             f"{defaults[0]}\' conversion supported.")
    return stands


__all__ = ['preproc_filter',
           'compute_location_metadata',
           'generate_reference_trees',
           'supplement_missing_tree_heights',
           'supplement_missing_tree_ages',
           'supplement_missing_stratum_diameters',
           'generate_sapling_trees_from_sapling_strata',
           'scale_area_weight',
           'convert_coordinates',
           'vectorize']
