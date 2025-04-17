control_structure = {
  "operation_params": {
    "inc": [
      {"incrementation": 1},
      {"incrementation": 2}
    ]
  },
  "simulation_events": [
    {
      "time_points": [1, 2],
      "generators": [
        {"sequence": ["do_nothing"]},
        {"alternatives": ["do_nothing", "inc"]}
      ]
    }
  ]
}
