from lukefi.metsi.domain.conditions import MinimumTimeInterval
from lukefi.metsi.sim.simulation_instruction import SimulationInstruction
from lukefi.metsi.sim.generators import Alternatives, Sequence, Event
from lukefi.metsi.sim.operations import do_nothing
from tests.test_utils import collecting_increment


control_structure = {
    "simulation_events": [
        SimulationInstruction(
            time_points=[1, 2, 3, 4],
            events=Sequence([
                Sequence([
                    Event(do_nothing),
                ]),
                Alternatives([
                    Event(do_nothing),
                    Event(
                        preconditions=[
                            MinimumTimeInterval(2, collecting_increment)
                        ],
                        treatment=collecting_increment
                    )
                ])
            ])
        )
    ]
}
