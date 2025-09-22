from lukefi.metsi.domain.conditions import MinimumTimeInterval
from lukefi.metsi.domain.forestry_operations.thinning import first_thinning
from lukefi.metsi.domain.pre_ops import convert_coordinates, generate_reference_trees, preproc_filter
from lukefi.metsi.domain.events import (
    CalculateBiomass,
    CalculateNpv,
    Clearcutting,
    CollectFelledTreeProperties,
    CollectStandingTreeProperties,
    CrossCutFelledTrees,
    CrossCutStandingTrees,
    DoNothing,
    EvenThinning,
    FirstThinning,
    GrowActa,
    Planting,
    ReportCollectives,
    ReportPeriod,
    ReportState,
    ThinningFromAbove,
    ThinningFromBelow)
from lukefi.metsi.sim.simulation_instruction import SimulationInstruction
from lukefi.metsi.sim.generators import Alternatives, Sequence


YEAR_START = 2025
STEP = 5
PERIOD = 10
# nperiods = 5
NPERIODS = 1
# year_final = 2075
YEAR_FINAL = YEAR_START + NPERIODS * PERIOD
# years_np = [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2065, 2070]
YEARS_NP = [YEAR_START + i * STEP for i in range(0, 2 * NPERIODS)]
# years_events = [2030, 2040, 2050, 2060, 2070]
YEARS_EVENTS = [YEAR_START + STEP + i * PERIOD for i in range(0, NPERIODS)]
# years_report = [2025, 2035, 2045, 2055, 2065, 2075]
YEARS_REPORT = [YEAR_START + i * PERIOD for i in range(0, NPERIODS + 1)]

operations_report = Sequence([
    CrossCutStandingTrees(
        file_parameters={
            "timber_price_table": "data/parameter_files/timber_price_table.csv"
        }
    ),
    CollectStandingTreeProperties(
        parameters={
            "properties": ["stems_per_ha", "species", "breast_height_diameter", "height",
                           "breast_height_age", "biological_age", "saw_log_volume_reduction_factor"]
        }
    ),
    CalculateNpv(
        parameters={
            "interest_rates": [1, 2, 3, 4, 5]
        },
        file_parameters={
            "land_values": "data/parameter_files/land_values_per_site_type_and_interest_rate.json",
            "renewal_costs": "data/parameter_files/renewal_operation_pricing.csv"
        },
    ),
    CalculateBiomass(
        parameters={
            "model_set": 1
        }
    ),
    ReportState()
])

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

    # Optional parameters to split Stands into batches before simulation, uncomment to use
    "slice_percentage": 10,
    # "slice_size": 50,


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
                "remove stands": "(site_type_category == None) or (site_type_category == 0)",  # not reference_trees
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
        SimulationInstruction(
            time_points=[YEAR_START],
            events=Sequence([
                Planting(
                    parameters={
                        "tree_count": 10
                    },
                    file_parameters={
                        "planting_instructions": "data/parameter_files/planting_instructions.txt"
                    }
                )
            ])
        ),
        SimulationInstruction(
            time_points=YEARS_REPORT,
            events=[operations_report]
        ),
        SimulationInstruction(
            time_points=YEARS_EVENTS,
            events=[
                Alternatives([
                    DoNothing(),
                    ThinningFromAbove(
                        parameters={
                            "thinning_factor": 0.98,
                            "e": 0.2
                        },
                        file_parameters={
                            "thinning_limits": "data/parameter_files/Thin.txt"
                        }
                    ),
                    FirstThinning(
                        preconditions=[
                            MinimumTimeInterval(50, first_thinning)
                        ],
                        parameters={
                            "thinning_factor": 0.97,
                            "e": 0.2,
                            "dominant_height_lower_bound": 11,
                            "dominant_height_upper_bound": 16
                        }
                    ),
                ]),
                Sequence([
                    CrossCutFelledTrees(
                        file_parameters={
                            "timber_price_table": "data/parameter_files/timber_price_table.csv"
                        }
                    ),
                    CollectFelledTreeProperties(
                        parameters={
                            "properties": ["stems_per_ha", "species", "breast_height_diameter", "height"]
                        }
                    )
                ])
            ]
        ),
        SimulationInstruction(
            time_points=YEARS_REPORT,
            events=[
                ReportPeriod()
            ]
        ),
        SimulationInstruction(
            time_points=[YEAR_FINAL],
            events=[
                ReportCollectives(
                    parameters={
                        "identifier": "identifier",
                        "npv_1_percent": "net_present_value.value[(net_present_value.interest_rate==1) & "
                        "(net_present_value.time_point == 2055)]",
                        "npv_2_percent": "net_present_value.value[(net_present_value.interest_rate==2) & "
                        "(net_present_value.time_point == 2055)]",
                        "npv_3_percent": "net_present_value.value[(net_present_value.interest_rate==3) & "
                        "(net_present_value.time_point == 2055)]",
                        "npv_4_percent": "net_present_value.value[(net_present_value.interest_rate==4) & "
                        "(net_present_value.time_point == 2055)]",
                        "npv_5_percent": "net_present_value.value[(net_present_value.interest_rate==5) & "
                        "(net_present_value.time_point == 2075)]",
                        "stock_0": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                        "(cross_cutting.time_point == 2025)]",
                        "stock_1": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                        "(cross_cutting.time_point == 2035)]",
                        "stock_2": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                        "(cross_cutting.time_point == 2045)]",
                        "stock_3": "cross_cutting.volume_per_ha[(cross_cutting.source == 'standing') & "
                        "(cross_cutting.time_point == 2055)]",
                        "harvest_period_1": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                        "(cross_cutting.time_point >= 2025) & "
                        "(cross_cutting.time_point < 2035)]",
                        "harvest_period_2": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                        "(cross_cutting.time_point >= 2035) & "
                        "(cross_cutting.time_point < 2045)]",
                        "harvest_period_3": "cross_cutting.volume_per_ha[(cross_cutting.source == 'harvested') & "
                        "(cross_cutting.time_point >= 2045) & "
                        "(cross_cutting.time_point < 2055)]"
                    }
                )
            ]
        ),
        SimulationInstruction(
            time_points=YEARS_NP,
            events=[
                GrowActa()
            ]
        )
    ],
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
