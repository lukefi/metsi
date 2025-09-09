from lukefi.metsi.sim.event import Event
from lukefi.metsi.sim.generators import Sequence, Treatment
from tests.test_utils import collecting_increment


control_structure = {
    "simulation_events": [
        Event(
            time_points=[1, 2, 3, 4],
            treatments=Sequence([
                Treatment(collecting_increment, parameters={"incrementation": 2})
            ])
        )
    ]
}
