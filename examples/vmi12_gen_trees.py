""" This declaration is used to define the output content of the preprocessing results """

from examples.declarations.export_prepro import default_csv

control_structure = {
  "app_configuration": {
    "state_format": "vmi12",
    "strategy": "partial",
    "run_modes": ["preprocess", "export_prepro"]
  },
  "preprocessing_params": {
    "generate_reference_trees": [
      {
        "n_trees": 10,
        "method": "weibull"
      }
    ]
  },
  "preprocessing_operations": ["generate_reference_trees"]
}

control_structure['export_prepro'] = {}
control_structure['export_prepro'].update(default_csv)


__all__ = ['control_structure']