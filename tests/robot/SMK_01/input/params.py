from tests.robot.SMK_01.input.collectives import collectives
from lukefi.metsi.domain.pre_ops import *
from lukefi.metsi.domain.sim_ops import *
from lukefi.metsi.sim.generators import *


params = {
    first_thinning: [
        {
            "thinning_factor": 0.97,
            "e": 0.2,
            "dominant_height_lower_bound": 11,
            "dominant_height_upper_bound": 16
        }
    ],
    thinning_from_below: [
        {
            "thinning_factor": 0.97,
            "e": 0.2
        }
    ],
    thinning_from_above: [
        {
            "thinning_factor": 0.98,
            "e": 0.2
        }
    ],
    even_thinning: [
        {
            "thinning_factor": 0.9,
            "e": 0.2
        }
    ],
    calculate_biomass: [
        {"model_set": 1}
    ],
    report_collectives: [collectives],
    report_period: [
        {"overall_volume": "cross_cutting.volume_per_ha"}
    ],
    calculate_npv: [
        {"interest_rates": [1, 2, 3, 4, 5]}
    ],
    collect_standing_tree_properties: [
        {"properties": ["stems_per_ha", "species", "breast_height_diameter", "height",
                        "breast_height_age", "biological_age", "saw_log_volume_reduction_factor"]}
    ],
    collect_felled_tree_properties: [
        {"properties": ["stems_per_ha", "species", "breast_height_diameter", "height"]}
    ],
    planting: [
        {"tree_count": 10}
    ]
}

param_files = {
    thinning_from_above: {
        "thinning_limits": "data/parameter_files/Thin.txt"
    },
    cross_cut_felled_trees: {
        "timber_price_table": "data/parameter_files/timber_price_table.csv"
    },
    cross_cut_standing_trees: {
        "timber_price_table": "data/parameter_files/timber_price_table.csv"
    },
    clearcutting: {
        "clearcutting_limits_ages": "data/parameter_files/renewal_ages_southernFI.txt",
        "clearcutting_limits_diameters": "data/parameter_files/renewal_diameters_southernFI.txt"
    },
    planting: {
        "planting_instructions": "data/parameter_files/planting_instructions.txt"
    },
    calculate_npv: {
        "land_values": "data/parameter_files/land_values_per_site_type_and_interest_rate.json",
        "renewal_costs": "data/parameter_files/renewal_operation_pricing.csv"
    }
}
