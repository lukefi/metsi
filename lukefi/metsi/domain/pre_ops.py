from lukefi.metsi.data.enums.internal import LandUseCategory
from lukefi.metsi.data.model import ForestStand, TreeStratum
from lukefi.metsi.forestry.forestry_utils import find_matching_storey_stratum_for_tree
from lukefi.metsi.forestry.preprocessing import tree_generation, pre_util
from lukefi.metsi.forestry.preprocessing.age_supplementing import supplement_age_for_reference_trees
from lukefi.metsi.forestry.preprocessing.naslund import naslund_height
from lukefi.metsi.domain.utils.filter import applyfilter
from lukefi.metsi.forestry.preprocessing.tree_generation import trees_from_sapling_height_distribution
from lukefi.metsi.forestry.preprocessing.tree_generation_lm import tree_generation_lm
from lukefi.metsi.forestry.preprocessing.tree_generation_validation import create_stratum_tree_comparison_set, \
    debug_output_row_from_comparison_set, debug_output_header_row
import traceback


def preproc_filter(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    named = operation_params.get("named", {})
    for k,v in operation_params.items():
        if k != "named":
            stands = applyfilter(stands, k, v, named)
    return stands


def compute_location_metadata(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """
    This operation sets in-place the location based metadata properties for each given ForestStand, where missing.
    These properties are: height above sea level, temperature sum, sea effect, lake effect, monthly temperature and
    monthly rainfall
    """
    # import constrained to here as pymotti is an optional dependency
    from pymotti.lasum import ilmanor
    from pymotti.coord import etrs_tm35_to_ykj as conv
    from pymotti.kor import xkor

    for stand in stands:
        if stand.geo_location[3] == 'EPSG:3067':
            lat, lon = conv(stand.geo_location[0] / 1000, stand.geo_location[1] / 1000)
        elif stand.geo_location[3] == 'EPSG:2393':
            lat, lon = (stand.geo_location[0] / 1000, stand.geo_location[1] / 1000)
        else:
            raise Exception("Unsupported CRS {} for stand {}".format(stand.geo_location[3], stand.identifier))

        if stand.geo_location[2] is None:
            stand.geo_location = (
                stand.geo_location[0],
                stand.geo_location[1],
                xkor(lat, lon),
                stand.geo_location[3]
            )
        wi = ilmanor(lon, lat, stand.geo_location[2])

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




def generate_reference_trees(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """ Operation function that generates (N * stratum) reference trees for each stand """
    debug = operation_params.get('debug', False)
    debug_output_rows = []
    debug_strata_rows = []
    debug_tree_rows = []
    method = operation_params.get('method', 'weibull')
    n_trees = operation_params.get('n_trees', 10)
    lm_mode = operation_params.get('lm_mode', 'dcons')
    lm_shdef = operation_params.get('lm_shdef', 'dcons')
    for i, stand in enumerate(stands):
        print(f"\rGenerating trees for stand {i}/{len(stands)}", end="")
        stand_trees = sorted(stand.reference_trees, key=lambda tree: tree.identifier)
        for tree in stand_trees:
            stratum = find_matching_storey_stratum_for_tree(tree, stand.tree_strata)
            if stratum is None:
                continue
            if stratum.__dict__.get('_trees') is not None:
                stratum._trees.append(tree)
            else:
                stratum._trees = [tree]
            if debug:
                debug_tree_rows.append([
                    stratum.identifier,
                    tree.breast_height_diameter or 'NA',
                    tree.height or 'NA',
                    tree.biological_age or 'NA',
                    tree.measured_height or 'NA'
                ])
        stand.tree_strata.sort(key=lambda stratum: stratum.identifier)
        new_trees = []
        for stratum in stand.tree_strata:
            stratum_trees = []
            if method == 'weibull':
                if pre_util.stratum_needs_diameter(stratum):
                    stratum = pre_util.supplement_mean_diameter(stratum)
                stratum_trees = tree_generation.reference_trees_from_tree_stratum(stratum, n_trees)
                stratum_trees = pre_util.scale_stems_per_ha(stratum_trees, stand.stems_per_ha_scaling_factors)
            elif method == 'lm':
                try:
                    if stratum.has_height_over_130_cm() and stratum.has_diameter():
                        stratum_trees = tree_generation_lm(stratum, stand.degree_days, stand.basal_area, n_trees, lm_mode, lm_shdef)
                    elif stratum.mean_height and stratum.mean_height <= 1.3:
                        stratum_trees = trees_from_sapling_height_distribution(stratum, n_trees)
                    else:
                        print(f"\nStratum {stratum.identifier} has no height or diameter usable for generating trees")
                        continue
                except Exception as e:
                    print(f"\nError generating trees for stratum {stratum.identifier} with diameter {stratum.mean_diameter}, height {stratum.mean_height}, basal_area {stratum.basal_area}")
                    print()
                    if debug:
                        traceback.print_exc()
                    else:
                        raise e
            stand_tree_count = len(new_trees)
            for i, tree in enumerate(stratum_trees):
                tree.identifier = "{}-{}-tree".format(stand.identifier, stand_tree_count + i + 1)
                new_trees.append(tree)
            validation_set = create_stratum_tree_comparison_set(stratum, stratum_trees)

            if debug:
                debug_strata_rows.append([
                    stratum.identifier,
                    stratum.mean_diameter,
                    stratum.mean_height,
                    stratum.basal_area,
                    stratum.stems_per_ha,
                    stratum.species.value,
                    stand.degree_days
                ])
                debug_output_rows.append(debug_output_row_from_comparison_set(stratum, validation_set))
        stand.reference_trees = new_trees
    print()
    if debug:
        import csv
        with open('debug_generated_tree_results.csv', 'w', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(debug_output_header_row())
            writer.writerows(debug_output_rows)
        if len(debug_strata_rows) > 1:
            with open('r_strata.dat', 'w', newline='\n') as stratum_file:
                writer = csv.writer(stratum_file, delimiter=' ')
                writer.writerow(["stratum", "D", "H", "G", "F", "age", "spe", "ddy"])
                writer.writerows(debug_strata_rows)
        if len(debug_tree_rows) > 1:
            with open('r_trees.dat', 'w', newline='\n') as tree_file:
                writer = csv.writer(tree_file, delimiter=' ')
                writer.writerow(["stratum", "d", "h", "age_measured", "h_measured"])
                writer.writerows(debug_tree_rows)
    return stands


def supplement_missing_tree_heights(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """ Fill in missing (None or nonpositive) tree heights from Näslund height curve """
    for stand in stands:
        for tree in stand.reference_trees:
            if (tree.height or 0) <= 0:
                tree.height = naslund_height(tree.breast_height_diameter, tree.species)
    return stands


def supplement_missing_tree_ages(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """ Attempt to fill in missing (None or nonpositive) tree ages using strata ages or other reference tree ages"""
    for stand in stands:
        supplement_age_for_reference_trees(stand.reference_trees, stand.tree_strata)
    return stands


def supplement_missing_stratum_diameters(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """ Attempt to fill in missing (None) stratum mean diameters using mean height """
    for stand in stands:
        for stratum in stand.tree_strata:
            if stratum.mean_diameter is None:
                if stratum.has_height_over_130_cm() and stand.land_use_category == LandUseCategory.SCRUB_LAND:
                    pre_util.supplement_mean_diameter(stratum)
    return stands


def generate_sapling_trees_from_sapling_strata(stands: list[ForestStand], **operation_params) -> list[ForestStand]:
    """ Create sapling reference trees from sapling strata """
    for stand in stands:
        for stratum in stand.tree_strata:
            if stratum.sapling_stratum:
                sapling = stratum.to_sapling_reference_tree()
                stand.reference_trees.append(sapling)
                sapling.stand = stand
                tree_number = len(stand.reference_trees) + 1
                sapling.identifier = "{}-{}-tree".format(stand.identifier, tree_number)
    return stands


operation_lookup = {
    'filter': preproc_filter,
    'compute_location_metadata': compute_location_metadata,
    'generate_reference_trees': generate_reference_trees,
    'supplement_missing_tree_heights': supplement_missing_tree_heights,
    'supplement_missing_tree_ages': supplement_missing_tree_ages,
    'supplement_missing_stratum_diameters': supplement_missing_stratum_diameters,
    'generate_sapling_trees_from_sapling_strata': generate_sapling_trees_from_sapling_strata
}
