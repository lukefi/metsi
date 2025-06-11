from lukefi.metsi.sim.operations import do_nothing
from tests.test_utils import collecting_increment


control_structure = {
  "operation_params": {
    collecting_increment: [
      {"incrementation": 1},
      {"incrementation": 2}
    ]
  },
  "simulation_events": [
    {
      "time_points": [1, 2],
      "generators": [
        {"sequence": [do_nothing]},
        {"alternatives": [do_nothing, collecting_increment]}
      ]
    }
  ]
}
