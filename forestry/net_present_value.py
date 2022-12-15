from sim.core_types import OpTuple
from forestdatamodel.model import ForestStand
from forestry.cross_cutting import CrossCutResult
from forestry.renewal import PriceableOperationInfo
from forestry.utils import get_renewal_costs_as_dict, get_land_values_as_dict



def _get_bare_land_value(filepath: str, soil_peatland_category: int, site_type: int, interest_rate: float) -> float:
    
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
    
    land_values = get_land_values_as_dict(filepath)
    soil_peatland_key = SOIL_PEATLAND_CATEGORY_MAPPING.get(soil_peatland_category)
    site_type_key = SITE_TYPE_MAPPING.get(site_type)
    land_value = land_values[soil_peatland_key][site_type_key][str(interest_rate)]
    return land_value        

def _discount_factor(r: float, t: int) -> float:
    return (1+r)**t

def calculate_npv(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """
    Expects that the relevant cross cut operations have been done before this.
    Expects interest rates to be given as a decimal (e.g. 0.05) and that the interest rates in the land values file correspond to these values.
    """
    stand, simulation_aggregates = payload

    cc_results = simulation_aggregates.get("cross_cutting")
    renewal_results = simulation_aggregates.get("renewal")

    interest_rates: list = operation_parameters["interest_rates"]
    land_values_file = operation_parameters["land_values"]
    renewal_costs_file = operation_parameters["renewal_costs"]
    
    NPVs_per_rate: dict[str, float] = {}

    for r in interest_rates:
        r = float(r)
        npv = 0.0

        # 1. add revenues
        x: CrossCutResult
        for x in cc_results:
            discounted_revenue = x.get_real_value() / _discount_factor(r, x.time_point)
            npv += discounted_revenue
        
        # 2. subtract costs
        y: PriceableOperationInfo
        for y in renewal_results:
            unit_cost = get_renewal_costs_as_dict(renewal_costs_file)[y.operation_name]
            discounted_cost = y.get_real_cost(unit_cost) / _discount_factor(r, y.time_point)
            npv -= discounted_cost
        
        # 4. add discounted bare land value
        npv += _get_bare_land_value(land_values_file, stand.soil_peatland_category, stand.site_type_category, r)
               
        NPVs_per_rate[str(r)] = npv

    simulation_aggregates.store("net_present_value", NPVs_per_rate)

    return payload
