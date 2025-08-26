from tests.robot.SMK_01.input.params import params, param_files
from lukefi.metsi.domain.pre_ops import *
from lukefi.metsi.domain.sim_ops import *
from lukefi.metsi.sim.generators import *


YEAR_STAR = 2025
STEP = 5
PERIOD = 10
NPERIODS = 1
YEAR_FINAL = YEAR_STAR + NPERIODS*PERIOD
years_np = [YEAR_STAR + i*STEP for i in range(0, 2*NPERIODS)]
years_events = [YEAR_STAR + STEP + i*PERIOD for i in range(0, NPERIODS)]
years_report = [YEAR_STAR + i*PERIOD for i in range(0, NPERIODS+1)]

operations_report = {sequence: [
    cross_cut_standing_trees,
    collect_standing_tree_properties,
    calculate_npv,
    calculate_biomass,
    report_state
]}

export_J = {
    "format": "J",
    "cvariables": [
        "identifier", "year", "site_type_category", "land_use_category", "soil_peatland_category"
    ],
    "xvariables": [
        "identifier", "npv_1_percent", "npv_2_percent", "npv_3_percent", "npv_4_percent", "npv_5_percent",
        "stock_0", "stock_1", "stock_2", "stock_3",
        "harvest_period_1", "harvest_period_2", "harvest_period_3"
    ]
}

control_structure = {
    "app_configuration": {
        "state_format": "xml",  # options: fdm, vmi12, vmi13, xml, gpkg
        "strata_origin": 2,
        "state_input_container": "json",  # Only relevant with fdm state_format. Options: pickle, json
        # "state_output_container": "csv",  # options: pickle, json, csv, null
        # "derived_data_output_container": "pickle",  # options: pickle, json, null
        "formation_strategy": "full",
        "evaluation_strategy": "depth",
        "run_modes": ["preprocess", "export_prepro", "simulate", "export"]
    },

    ## Optional parameters to split Stands into batches before simulation, uncomment to use
    "slice_percentage": 10,
    #"slice_size": 50,


    # Preprocessing control declaration
    "preprocessing_operations": [
        convert_coordinates,
        generate_reference_trees,  # reference trees from strata, replaces existing reference trees
        preproc_filter
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
    'export_prepro': {
        "csv": {},  # default csv export
        "rst": {},
        "json": {}
    },

    # Simulation control declaration
    "simulation_events": [
        {
            "time_points": [YEAR_STAR],
            "generators": [
                {sequence: [planting]}
            ]
        },
        {
            "time_points": years_report,  # data for reporting
            "generators": [operations_report]
        },
        {
            "time_points": years_events,
            "generators": [
                {
                    alternatives: [
                        do_nothing,
                        thinning_from_above,
                        first_thinning,
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
            "time_points": years_report,
            "generators": [
                {sequence: [report_period]}
            ]
        },
        {
            "time_points": [YEAR_FINAL],
            "generators": [
                {sequence: [report_collectives]}
            ]
        },
        {
            "time_points": years_np,
            "generators": [
                {sequence: [grow_acta]}
            ]
        }
    ],
    "operation_params": params,
    "operation_file_params": param_files,
    "run_constraints": {
        first_thinning: {
            "minimum_time_interval": 50
        },
        clearcutting: {
            "minimum_time_interval": 50
        }
    },
    "export": [
        export_J,
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
__all__ = ['control_structure']
