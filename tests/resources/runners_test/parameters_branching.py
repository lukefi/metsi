from lukefi.metsi.sim.simulation_instruction import SimulationInstruction
from lukefi.metsi.sim.generators import Alternatives, Sequence, Event
from lukefi.metsi.sim.operations import do_nothing
from tests.test_utils import collecting_increment


control_structure = {
    "simulation_instructions": [
        SimulationInstruction(
            time_points=[1, 2],
            events=Sequence([
                Sequence([Event(do_nothing)]),
                Alternatives([
                    Event(do_nothing),
                    Event(collecting_increment, parameters={"incrementation": 1}),
                    Event(collecting_increment, parameters={"incrementation": 2})
                ])
            ])
        )
    ]
}
