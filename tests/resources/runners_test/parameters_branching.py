from lukefi.metsi.sim.event import Event
from lukefi.metsi.sim.generators import Alternatives, Sequence, Treatment
from lukefi.metsi.sim.operations import do_nothing
from tests.test_utils import collecting_increment


control_structure = {
    "simulation_events": [
        Event(
            time_points=[1, 2],
            treatments=Sequence([
                Sequence([Treatment(do_nothing)]),
                Alternatives([
                    Treatment(do_nothing),
                    Treatment(collecting_increment, parameters={"incrementation": 1}),
                    Treatment(collecting_increment, parameters={"incrementation": 2})
                ])
            ])
        )
    ]
}
