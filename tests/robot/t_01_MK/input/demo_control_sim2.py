from tests.robot.t_01_MK.input.params import params, param_files

year_start = 2025

step = 5
period = 10
#nperiods = 5
nperiods = 3
#year_final = 2075
year_final = year_start + nperiods*period
#years_np = [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2065, 2070]
years_np = [year_start + i*step for i in range(0,2*nperiods)]
#years_events = [2030, 2040, 2050, 2060, 2070]
years_events = [year_start + step + i*period for i in range(0,nperiods)]
#years_report = [2025, 2035, 2045, 2055, 2065, 2075]
years_report = [year_start + i*period for i in range(0,nperiods+1)]

operations_report = {"sequence": [
                    "cross_cut_standing_trees",
                    "collect_standing_tree_properties",
                    "calculate_npv",
                    "calculate_biomass",
                    "report_state"
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
        "state_format": "fdm",  # options: fdm, vmi12, vmi13, xml, gpkg
        "state_input_container": "json",  # Only relevant with fdm state_format. Options: pickle, json
        # "state_output_container": "csv",  # options: pickle, json, csv, null
        # "derived_data_output_container": "pickle",  # options: pickle, json, null
        "formation_strategy": "full",
        "evaluation_strategy": "depth",
        "run_modes": ["simulate", "export"]
    },
    "simulation_events": [
        {
            "time_points": [year_start],
            "generators": [
                {"sequence": ["planting"]}
            ]
        },
        {
            "time_points": years_report, # data for reporting
            "generators": [operations_report]
        },
        {
            "time_points": years_events,
            "generators": [
                {
                    "alternatives": [
                        "do_nothing",
                        "thinning_from_below",
                        "thinning_from_above",
                        "first_thinning",
                        "even_thinning",
                        {
                            "sequence": [
                                "clearcutting",
                                "planting"
                            ]
                        }
                    ]
                },
                { 
                    "sequence": [
                        "cross_cut_felled_trees",
                        "collect_felled_tree_properties"
                    ]
                }
            ]
        },
        {
            "time_points": years_report,
            "generators": [
                {"sequence": ["report_period"]}
            ]
        },
        {
            "time_points": [year_final],
            "generators": [
                {"sequence": ["report_collectives"]}
            ]
        },
        {
            "time_points": years_np,
            "generators": [
                {"sequence": ["grow_acta"]}
                # "grow_motti"
            ]
        }
    ],
    "operation_params": params,
    "operation_file_params": param_files ,
    "run_constraints": {
        "first_thinning": {
            "minimum_time_interval": 50
        },
        "clearcutting": {
            "minimum_time_interval": 50
        }
    },
    "export": [ export_J,
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
__all__ =['control_structure']
