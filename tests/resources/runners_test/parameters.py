from lukefi.metsi.sim.generators import sequence
from tests.test_utils import collecting_increment


control_structure = {
  "operation_params": {
    collecting_increment: [
      {"incrementation": 2}
    ]
  },
  "simulation_events": [
    {
      "time_points": [1, 2, 3, 4],
      "generators": [
        {
          sequence: [
            collecting_increment
          ]
        }
      ]
    }
  ]
}
