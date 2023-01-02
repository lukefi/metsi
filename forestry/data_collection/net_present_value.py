from sim.core_types import CollectedData, OpTuple
from lukefi.metsi.data.model import ForestStand
from forestry.collected_types import CrossCutResult, NPVResult, PriceableOperationInfo
from forestry.utils.file_io import get_renewal_costs_as_dict, get_land_values_as_dict


def _get_bare_land_value(land_values: dict, soil_peatland_category: int, site_type: int, interest_rate: int) -> float:

    SOIL_PEATLAND_CATEGORY_MAPPING = {
        1: "mineral_soils",
        2: "spruce_mires",
        3: "pine_mires",
        4: "treeless_mires",
        5: "treeless_mires"
    }

    SITE_TYPE_MAPPING = {
        1: "very_rich_sites",
        2: "rich_sites",
        3: "damp_sites",
        4: "sub_dry_sites",
        5: "dry_sites",
        6: "barren_sites",
        7: "rocky_or_sandy",
        8: "open_mountains"
    }

    soil_peatland_key = SOIL_PEATLAND_CATEGORY_MAPPING.get(soil_peatland_category)
    site_type_key = SITE_TYPE_MAPPING.get(site_type)
    land_value = land_values[soil_peatland_key][site_type_key][str(interest_rate)]
    return land_value


def _discount_factor(r: float, current_time_point: int, initial_time_point) -> float:
    t = current_time_point - initial_time_point
    return (1+r)**t


def _calculate_npv_for_rate(
    stand: ForestStand,
    collected_data: CollectedData,
    land_values: dict,
    renewal_costs: dict,
    int_r: int
    ) -> float:

    cc_results = collected_data.get_list_result("cross_cutting")
    renewal_results = collected_data.get_list_result("renewal")
    current_time_point = collected_data.current_time_point
    initial_time_point = collected_data.initial_time_point

    r = int_r/100
    npv = 0.0

    # 1. add revenues from harvesting. This excludes results from cross_cut_standing_trees.
    x: CrossCutResult
    for x in filter(lambda x: x.source == "harvested", cc_results):
        discounted_revenue = x.get_real_value() / _discount_factor(r, x.time_point, initial_time_point)
        npv += discounted_revenue

    # 2. add discounted value of standing tree stock at the current time point.
    standing_cc_results = list(filter(lambda x: x.source == "standing" and x.time_point == current_time_point, cc_results))
    if len(stand.reference_trees) > 0 and len(standing_cc_results) == 0:
        raise UserWarning("NPV calculation did not find cross cut results for standing trees. Did you forget to declare the 'cross_cut_standing_trees' operation before 'calculate_npv'?")
    else:
        y: CrossCutResult
        for y in standing_cc_results:
            discounted_revenue = y.get_real_value() / _discount_factor(r, current_time_point, initial_time_point)
            npv += discounted_revenue

    # 3. subtract costs
    z: PriceableOperationInfo
    for z in renewal_results:
        unit_cost = renewal_costs[z.operation]
        discounted_cost = z.get_real_cost(unit_cost) / _discount_factor(r, z.time_point, initial_time_point)
        npv -= discounted_cost

    # 4. add discounted bare land value
    npv += _get_bare_land_value(land_values, stand.soil_peatland_category, stand.site_type_category, int_r)
    return npv


def calculate_npv(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Expects that the relevant cross cut operations have been done before this.
    Expects interest rates to be given as integers (e.g. 5) and that the interest rates in the land values file correspond to these values.
    """
    stand, collected_data = payload

    interest_rates: list = operation_parameters["interest_rates"]
    land_values = get_land_values_as_dict(operation_parameters["land_values"])
    renewal_costs = get_renewal_costs_as_dict(operation_parameters["renewal_costs"])

    for int_r in interest_rates:
        npv = _calculate_npv_for_rate(stand, collected_data, land_values, renewal_costs, int_r)
        npv_data = NPVResult(collected_data.current_time_point, int_r, npv)
        collected_data.extend_list_result("net_present_value", [npv_data])

    return payload

