from lukefi.metsi.sim.operations import do_nothing
from tests.test_utils import collecting_increment


control_structure = {
  "run_constraints": {
    collecting_increment: {
      "minimum_time_interval": 2
    }
  },
  "simulation_events": [
    {
      "time_points": [1, 2, 3, 4],
      "generators": [
        {
          "sequence": [
            do_nothing
          ]
        },
        {
          "alternatives": [
            do_nothing,
            collecting_increment
          ]
        }
      ]
    }
  ]
}
