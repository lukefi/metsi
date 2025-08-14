from examples.declarations.export_prepro import csv_and_json
from lukefi.metsi.domain.pre_ops import *
from lukefi.metsi.domain.sim_ops import *
from lukefi.metsi.sim.generators import *


control_structure = {
    "app_configuration": {
        "state_format": "vmi13",  # options: fdm, vmi12, vmi13, xml, gpkg
        # "state_input_container": "csv",  # Only relevant with fdm state_format. Options: pickle, json
        # "state_output_container": "csv",  # options: pickle, json, csv, null
        # "derived_data_output_container": "pickle",  # options: pickle, json, null
        "formation_strategy": "partial",
        "evaluation_strategy": "depth",
        "run_modes": ["preprocess", "export_prepro", "simulate", "postprocess", "export"]
    },
    "preprocessing_operations": [
        scale_area_weight,
        generate_reference_trees,  # reference trees from strata, replaces existing reference trees
        preproc_filter
        # "supplement_missing_tree_heights",
        # "supplement_missing_tree_ages",
        # "generate_sapling_trees_from_sapling_strata"
    ],
    "preprocessing_params": {
        generate_reference_trees: [
            {
                "n_trees": 10,
                "method": "weibull",
                "debug": False
            }
        ],
        preproc_filter: [
            {
                "remove trees": "sapling or stems_per_ha == 0",
                "remove stands": "site_type_category == 0",  # not reference_trees
                "remove stands": "site_type_category == None"
            }
        ]
    },
    "simulation_events": [
        {
            "time_points": [2020],
            "generators": [
                {sequence: [planting]}
            ]
        },
        {
            "time_points": [2020, 2025, 2030, 2035, 2040, 2045, 2050],
            "generators": [
                {sequence: [
                    cross_cut_standing_trees,
                    collect_standing_tree_properties,
                    calculate_npv,
                    calculate_biomass,
                    report_state
                ]}
            ]
        },
        {
            "time_points": [2035, 2045],
            "generators": [
                {
                    alternatives: [
                        do_nothing,
                        # "thinning_from_below",
                        # "thinning_from_above",
                        first_thinning,
                        even_thinning,
                        {
                            sequence: [
                                clearcutting,
                                planting
                                # operations for renewal after clearcutting go here
                            ]
                        }
                    ]
                },
                {
                    sequence: [
                        cross_cut_felled_trees,
                        collect_felled_tree_properties
                    ]
                }
            ]
        },
        {
            "time_points": [2020, 2030, 2040, 2050],
            "generators": [
                {sequence: [report_period]}
            ]
        },
        {
            "time_points": [2050],
            "generators": [
                {sequence: [report_collectives]}
            ]
        },
        {
            "time_points": [2020, 2025, 2030, 2035, 2040, 2045, 2050],
            "generators": [
                {sequence: [grow_acta]}
                # "grow_motti"
            ]
        }
    ],
    "operation_params": {
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
        report_collectives: [
            {
                "identifier": "identifier",
                "npv_1_percent": "net_present_value.value[(net_present_value.interest_rate==1) & "
                "(net_present_value.time_point == 2050)]",
                "npv_2_percent": "net_present_value.value[(net_present_value.interest_rate==2) & "
                "(net_present_value.time_point == 2050)]",
                "npv_3_percent": "net_present_value.value[(net_present_value.interest_rate==3) & "
                "(net_present_value.time_point == 2050)]",
                "npv_4_percent": "net_present_value.value[(net_present_value.interest_rate==4) & "
                "(net_present_value.time_point == 2050)]",
                "npv_5_percent": "net_present_value.value[(net_present_value.interest_rate==5) & "
                "(net_present_value.time_point == 2050)]",
                "stock_2020": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 2020)]",
                "stock_2030": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 2030)]",
                "stock_2040": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 2040)]",
                "stock_2050": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                "(cross_cutting.time_point == 2050)]",
                "harvest_2035": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 2035)]",
                "harvest_2045": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point == 2045)]",
                "harvest_period_2030": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point >= 2020) & (cross_cutting.time_point < 2030)]",
                "harvest_period_2040": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point >= 2030) & (cross_cutting.time_point < 2040)]",
                "harvest_period_2050": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                "(cross_cutting.time_point >= 2040) & (cross_cutting.time_point < 2050)]"
            }
        ],
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
    },
    "operation_file_params": {
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
    },
    "run_constraints": {
        first_thinning: {
            "minimum_time_interval": 50
        },
        clearcutting: {
            "minimum_time_interval": 50
        }
    },
    "post_processing": {
        "operation_params": {
            do_nothing: [
                {"param": "value"}
            ]
        },
        "post_processing": [
            do_nothing
        ]
    },
    "export": [
        {
            "format": "J",
            "cvariables": [
                "identifier", "year", "site_type_category", "land_use_category", "soil_peatland_category"
            ],
            "xvariables": [
                "identifier", "npv_1_percent", "npv_2_percent", "npv_3_percent", "npv_4_percent", "npv_5_percent",
                "stock_2020", "stock_2030", "stock_2040", "stock_2050",
                "harvest_2035", "harvest_2045",
                "harvest_period_2030", "harvest_period_2040", "harvest_period_2050"
            ]
        },
        {
            "format": "rm_schedules_events_timber",
            "filename": "timber_sums.txt"
        },
        {
            "format": "rm_schedules_events_trees",
            "filename": "trees.txt"
        }
    ]
}

# The preprocessing export format is added as an external module
control_structure['export_prepro'] = csv_and_json

__all__ = ['control_structure']
