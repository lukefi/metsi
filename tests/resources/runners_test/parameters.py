from lukefi.metsi.sim.simulation_instruction import SimulationInstruction
from lukefi.metsi.sim.generators import Sequence, Event
from tests.test_utils import collecting_increment


control_structure = {
    "simulation_events": [
        SimulationInstruction(
            time_points=[1, 2, 3, 4],
            events=Sequence([
                Event(collecting_increment, parameters={"incrementation": 2})
            ])
        )
    ]
}
