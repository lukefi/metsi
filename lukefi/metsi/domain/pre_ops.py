from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.forestry.preprocessing import tree_generation, pre_util
from lukefi.metsi.forestry.preprocessing.age_supplementing import supplement_age_for_reference_trees
from lukefi.metsi.forestry.preprocessing.naslund import naslund_height
from lukefi.metsi.domain.utils.filter import applyfilter
from lukefi.metsi.forestry.preprocessing.tree_generation_validation import create_stratum_tree_comparison_set, \
    debug_output_row_from_comparison_set, debug_output_header_row


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
    debug_filename = operation_params.get('debug_filename', 'debug_weibull_reference_trees.csv')

    n_trees = pre_util.get_or_default(operation_params['n_trees'])
    for stand in stands:
        stand_trees = []
        for stratum in stand.tree_strata:
            if pre_util.stratum_needs_diameter(stratum):
                stratum = pre_util.supplement_mean_diameter(stratum)
            stratum_trees = tree_generation.reference_trees_from_tree_stratum(stratum, n_trees)

            stratum_trees = pre_util.scale_stems_per_ha(stratum_trees, stand.stems_per_ha_scaling_factors)
            stand_tree_count = len(stand_trees)
            for i, tree in enumerate(stratum_trees):
                tree.identifier = "{}-{}-tree".format(stand.identifier, stand_tree_count + i + 1)
                stand_trees.append(tree)
            validation_set = create_stratum_tree_comparison_set(stratum, stratum_trees)

            if debug:
                debug_output_rows.append(debug_output_row_from_comparison_set(stratum, validation_set))
        stand.reference_trees = stand_trees
    if debug:
        import csv
        with open(debug_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(debug_output_header_row())
            writer.writerows(debug_output_rows)
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


operation_lookup = {
    'filter': preproc_filter,
    'compute_location_metadata': compute_location_metadata,
    'generate_reference_trees': generate_reference_trees,
    'supplement_missing_tree_heights': supplement_missing_tree_heights,
    'supplement_missing_tree_ages': supplement_missing_tree_ages
}
