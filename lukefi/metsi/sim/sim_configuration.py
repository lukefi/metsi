from types import SimpleNamespace
from lukefi.metsi.sim.event import Event, generator_declarations_for_time_point
from lukefi.metsi.sim.generators import Generator, Sequence


class SimConfiguration[T](SimpleNamespace):
    """
    A class to manage simulation configuration, including operations, generators,
    events, and time points.
    Attributes:
        events: A list of declared events for the simulation.
        time_points: A sorted list of unique time points derived from the
            declared simulation events.
    Methods:
        __init__(**kwargs):
            Initializes the SimConfiguration instance with operation and generator
            lookups, and additional keyword arguments.
    """
    events: list[Event[T]] = []
    time_points: list[int] = []

    def __init__(self, **kwargs):
        """
        Initializes the core simulation object.
        Args:
            **kwargs: Additional keyword arguments to be passed to the parent class initializer.
        """
        super().__init__(**kwargs)
        self._populate_simulation_events(self.simulation_events)

    def _populate_simulation_events(self, events: list["Event[T]"]):
        time_points = set()
        self.events = events
        for event in events:
            source_time_points = event.time_points
            time_points.update(source_time_points)
        self.time_points = sorted(time_points)

    def full_tree_generators(self) -> Generator[T]:
        """
        Create a NestableGenerator describing a single simulator run.

        :return: a list of prepared generator functions
        """
        wrapper = []
        for time_point in self.time_points:
            generator_declarations = generator_declarations_for_time_point(self.events, time_point)
            time_point_wrapper_declaration: Sequence[T] = Sequence(generator_declarations, time_point)
            wrapper.append(time_point_wrapper_declaration)
        return Sequence(wrapper, 0)

    def partial_tree_generators_by_time_point(self) -> dict[int, Generator[T]]:
        """
        Create a dict of NestableGenerators keyed by their time_point in the simulation. Used for generating
        partial EventTrees of the simulation.

        :return: a list of prepared generator functions
        """

        generators_by_time_point = {}

        for time_point in self.time_points:
            generator_declarations = generator_declarations_for_time_point(self.events, time_point)
            sequence_wrapper_declaration: Generator[T] = Sequence(generator_declarations, time_point)
            generators_by_time_point[time_point] = sequence_wrapper_declaration
        return generators_by_time_point
