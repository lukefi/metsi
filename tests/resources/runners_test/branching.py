control_structure = {
  "run_constraints": {
    "inc": {
      "minimum_time_interval": 2
    }
  },
  "simulation_events": [
    {
      "time_points": [1, 2, 3, 4],
      "generators": [
        {
          "sequence": [
            "do_nothing"
          ]
        },
        {
          "alternatives": [
            "do_nothing",
            "inc"
          ]
        }
      ]
    }
  ]
}
