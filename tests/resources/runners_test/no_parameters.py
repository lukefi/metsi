from tests.test_utils import collecting_increment


control_structure = {
  "simulation_events": [
    {
      "time_points": [1, 2, 3, 4],
      "generators": [
        {
          "sequence": [
            collecting_increment
          ]
        }
      ]
    }
  ]
}
