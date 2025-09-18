from lukefi.metsi.domain.conditions import MinimumTimeInterval
from lukefi.metsi.sim.event import Event
from lukefi.metsi.sim.generators import Alternatives, Sequence, Treatment
from lukefi.metsi.sim.operations import do_nothing
from tests.test_utils import collecting_increment


control_structure = {
    "simulation_events": [
        Event(
            time_points=[1, 2, 3, 4],
            treatments=Sequence([
                Sequence([
                    Treatment(do_nothing),
                ]),
                Alternatives([
                    Treatment(do_nothing),
                    Treatment(
                        preconditions=[
                            MinimumTimeInterval(2, collecting_increment)
                        ],
                        treatment_fn=collecting_increment
                    )
                ])
            ])
        )
    ]
}
