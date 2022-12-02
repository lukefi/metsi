from typing import Any, Callable, Optional
from sim.core_types import Step, SimConfiguration, SimulationEvent, OperationPayload, GeneratorFn
from sim.operations import prepared_processor, prepared_operation, resolve_operation
from sim.util import get_operation_file_params, merge_operation_params


class NestableGenerator:
    """
    NestableGenerator represents a tree for nested event generators in the simulation tree. Construction of this class
    creates a tree structure where leaf nodes represent actual GeneratorFn instances to populate a Step tree. The
    tree organization represents the nested sequences and alternatives structure in simulation events declaration.
    """
    prepared_generator: Optional[GeneratorFn] = None
    time_point: int = 0
    nested_generators: list['NestableGenerator']
    free_operations: list[dict or str]
    config: SimConfiguration

    def __init__(self,
                 config: SimConfiguration,
                 generator_declaration: dict,
                 time_point: int):
        """Construct a NestableGenerator for a given generator block within the SimConfiguration and for the given
        time point."""
        self.config = config
        self.generator_type = list(generator_declaration.keys())[0]
        self.time_point = time_point
        self.nested_generators = []
        self.free_operations = []
        children_tags = generator_declaration[self.generator_type]

        for child in children_tags:
            self.wrap_generator_candidate(child)

        if len(self.free_operations):
            if len(self.nested_generators) == 0:
                # leaf node, prepare the actual GeneratorFn
                prepared_operations = []
                for op in self.free_operations:
                    prepared_operations.extend(prepare_parametrized_operations(config, op, time_point))
                self.prepared_generator = generator_function(self.generator_type, GENERATOR_LOOKUP, *prepared_operations)
            else:
                self.wrap_free_operations()

    def wrap_generator_candidate(self, candidate):
        """Create NestableGenerators for nested generator declarations within current generator block. Separate
        individual operations as free operations into self state."""
        if isinstance(candidate, dict):
            # Encountered a nested generator.
            if list(candidate.keys())[0] in ('sequence', 'alternatives'):
                # Preceding free operations must be wrapped as NestableGenerators
                self.wrap_free_operations()
                self.nested_generators.append(NestableGenerator(self.config, candidate, self.time_point))
        elif isinstance(candidate, str):
            # Encountered an operation tag.
            self.free_operations.append(candidate)

    def wrap_free_operations(self):
        """Create NestableGenerators for individual operations collected into self state. Clear the list of operations
        afterwards."""
        if len(self.free_operations):
            if self.generator_type == 'alternatives':
                for operation in self.free_operations:
                    decl = {'sequence': [operation]}
                    self.nested_generators.append(NestableGenerator(self.config, decl, self.time_point))
            elif self.generator_type == 'sequence':
                decl = {'sequence': self.free_operations}
                self.nested_generators.append(NestableGenerator(self.config, decl, self.time_point))
            self.free_operations = []

    def unwrap(self, previous: list[Step]) -> list[Step]:
        """
        Recursive depth-first walkthrough of NestableGenerator tree starting from self to generate a list of Steps.
        These steps denote the leaves of the given Step trees as expanded by self.

        Sequence type NestableGenerators generate their tree of children Steps to follow up each of the given previous
        Steps in order. Idea is like "previous + next1,next2 => [previous, next1, next2]".

        Alternatives type NestableGenerators generate their tree of children Steps attaching a copy to each given
        previous Step. Idea is like "previous + next1,next2 => [previous, next1], [previous, next2]".

        Recursion end condition 1 is that self is a leaf that has a GeneratorFn that ultimately extends upon
        the previous Steps and returns the resulting list of Steps.

        Recursion end condition 2 is that a leaf that has no GeneratorFn or child NestableGenerators. Returns the
        previous Steps unaltered.

        :param previous: list of Steps denoting the Step tree at parent NestableGenerator or another Step root
        :return: list of Steps resulting from attempting to attach self's tree of Steps into previous Steps
        """
        if self.prepared_generator is not None:
            return self.prepared_generator(previous)
        elif len(self.nested_generators) == 0:
            return previous
        else:
            if self.generator_type == 'sequence':
                current = previous
                for child in self.nested_generators:
                    current = child.unwrap(current)
                return current
            elif self.generator_type == 'alternatives':
                current = []
                for child in self.nested_generators:
                    current.extend(child.unwrap(previous))
                return current
            return previous


def sequence(parents: Optional[list[Step]] = None, *operations: Callable) -> list[Step]:
    """
    Generate a linear sequence of steps, optionally extending each Step in the given list of Steps with it.
    :param parents: optional
    :param operations:
    :return:
    """
    result = []
    if parents is None or len(parents) == 0:
        parents = [Step()]
    for root_step in parents:
        previous_step = root_step
        for operation in operations:
            current_step = Step(operation, previous_step)
            previous_step.add_branch(current_step)
            previous_step = current_step
        result.append(previous_step)
    return result


def alternatives(parents: Optional[list[Step]] = None, *operations: Callable) -> list[Step]:
    """
    Generate branches for an optional list of steps, out of an *args list of given operations
    :param parents:
    :param operations:
    :return: a list of leaf steps now under the given parent steps
    """
    result = []
    if parents is None or len(parents) == 0:
        parents = [Step()]
    for step in parents:
        for operation in operations:
            branching_step = Step(operation, step)
            step.add_branch(branching_step)
            result.append(branching_step)
    return result


GENERATOR_LOOKUP = {
    'sequence': sequence,
    'alternatives': alternatives,
    }


def compose(*generators: GeneratorFn) -> Step:
    """
    Generate a simulation Step tree using the given list of generator functions

    :param generators: generator functions which produce sequences and branches ('alternatives') of Step function wrappers
    :return: The root node of the generated tree
    """
    root = Step()
    previous = [root]
    for generator in generators:
        current = generator(previous)
        previous = current
    return root


def compose_nested(nestable_generator: NestableGenerator) -> Step:
    """
    Generate a simulation Step tree using the given NestableGenerator.

    :param nestable_generator: NestableGenerator tree for generating a Step tree.
    :return: The root node of the generated Step tree
    """
    root = Step()
    nestable_generator.unwrap([root])
    return root


def repeat(times: int, *step_generators: GeneratorFn) -> list[GeneratorFn]:
    """
    For the given, positive, non-zero number of times, repeat the given list of generator functions and return them as
    a list.

    :param times: positive, non-zero integer for repetition count
    :param step_generators: functions to repeat in sequence
    :return:
    """
    if times < 1:
        raise Exception("Repetition count must be a positive integer value")
    result = []
    for i in range(0, times):
        for generator in step_generators:
            result.append(generator)
    return result


def simple_processable_chain(operation_tags: list[str], operation_params: dict, operation_lookup: dict) -> list[
    Callable]:
    """Prepare a list of partially applied (parametrized) operation functions based on given declaration of operation
    tags and operation parameters"""
    result = []
    for tag in operation_tags:
        params = operation_params.get(tag, [{}])
        if len(params) > 1:
            raise Exception("Trying to apply multiple parameter set for preprocessing operation \'{}\'. "
                "Defining multiple parameter sets is only supported for alternative clause generators.".format(tag))
        result.append(prepared_operation(resolve_operation(tag, operation_lookup), **params[0]))
    return result


def generator_declarations_for_time_point(events: list[SimulationEvent], time: int) -> list[dict]:
    """
    From simulation_steps, find the step generators declared for the given time point. Upon no match,
    a sequence of a single do_nothing operation is supplanted.

    :param events: list of SimulationEvent object for generator declarations and time points
    :param time: point of simulation time for selecting matching generators
    :return: list of generator declarations for the desired point of time
    """
    generator_declarations = []
    for generator_candidate in events:
        if time in generator_candidate.time_points:
            generator_declarations.extend(generator_candidate.generators)
    return generator_declarations


def generator_function(key, generator_lookup: dict, *processors: Callable) -> GeneratorFn:
    """Crate a generator function wrapper for function in generator_lookup by the key. Binds the
    argument list of processors with the generator."""
    return lambda parent_steps: generator_lookup[key](parent_steps, *processors)


def generate_time_series(simulation_events: list) -> list[int]:
    """Scan simulation_events for all unique time points and return them as an ascending ordered list. """
    time_points = set()
    for event_set in simulation_events:
        time_points.update(event_set['time_points'])
    return sorted(list(time_points))


def prepare_parametrized_operations(config: SimConfiguration,
                                    operation_tag: str,
                                    time_point: int) -> list[Callable[[Any], OperationPayload]]:
    parameter_set_choices = config.operation_params.get(operation_tag, [{}])
    operation_run_constraints = config.run_constraints.get(operation_tag)
    this_operation_file_params = get_operation_file_params(operation_tag, config.operation_file_params)
    results = []
    for parameter_set in parameter_set_choices:
        combined_params = merge_operation_params(parameter_set, this_operation_file_params)
        results.append(prepared_processor(
            operation_tag,
            config.operation_lookup,
            time_point,
            operation_run_constraints,
            **combined_params))
    return results


def full_tree_generators(config: SimConfiguration) -> NestableGenerator:
    """
    Creat a NestableGenerator describing a single simulator run.

    :param config: a prepared SimConfiguration object
    :return: a list of prepared generator functions
    """
    wrapper = NestableGenerator(config, {'sequence': []}, 0)
    for time_point in config.time_points:
        generator_declarations = generator_declarations_for_time_point(config.events, time_point)
        time_point_wrapper_declaration = {'sequence': generator_declarations}
        wrapper.nested_generators.append(NestableGenerator(config, time_point_wrapper_declaration, time_point))
    return wrapper


def partial_tree_generators_by_time_point(config: SimConfiguration) -> dict[int, NestableGenerator]:
    """
    Create a dict of NestableGenerators describing keyed by their time_point in the simulation. Used for generating
    partial step trees of the simulation.

    :param config: a prepared SimConfiguration object
    :return: a list of prepared generator functions
    """

    generators_by_time_point = {}

    for time_point in config.time_points:
        generator_declarations = generator_declarations_for_time_point(config.events, time_point)
        sequence_wrapper_declaration = {
            'sequence': generator_declarations
        }
        wrapper_generator = NestableGenerator(config, sequence_wrapper_declaration, time_point)
        generators_by_time_point[time_point] = wrapper_generator
    return generators_by_time_point

