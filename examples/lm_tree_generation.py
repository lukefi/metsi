from lukefi.metsi.domain.pre_ops import *
from lukefi.metsi.domain.sim_ops import *
from lukefi.metsi.sim.generators import *

control_structure = {
    "app_configuration": {
        "state_format": "vmi13",
        "measured_trees": True,
        "run_modes": ["preprocess", "export_prepro"]
    },

    "preprocessing_operations": [
        supplement_missing_stratum_diameters,
        preproc_filter,
        scale_area_weight,
        generate_reference_trees
    ],

    "preprocessing_params": {
        preproc_filter: [
            {
                "remove trees": "tree_type not in ('V', 'U', 'S', 'T', 'N')",
                "remove stands": "site_type_category is None"
            }
        ],
        generate_reference_trees: [
            {
                "n_trees": 10,
                "method": "lm",  # lm, weibull
                "stratum_association_diameter_threshold": 2.5,
                "lm_mode": "dcons",  # dcons, fcons
                "lm_shdef": 5,
                "debug": True  # true, false
            }
        ]
    },
    "export_prepro": {
        "csv": {}  # default csv export
    }
}

__all__ = ["control_structure"]
