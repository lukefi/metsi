from lukefi.metsi.domain.treatments import DoNothing
from lukefi.metsi.sim.event_tree import EventTree
from lukefi.metsi.sim.generators import Alternatives, Sequence


decl = Sequence([
    DoNothing(),
    Alternatives([
        DoNothing(),
        Sequence([
            DoNothing(),
            DoNothing()
        ]),
        Alternatives([
            Sequence([
                DoNothing(),
                DoNothing()
            ]),
            Sequence([
                DoNothing(),
                DoNothing(),
                DoNothing()
            ])
        ])
    ]),
    DoNothing()
])

root = EventTree()
decl.unwrap([root], 0)
root.print()
