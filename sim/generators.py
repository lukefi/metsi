from typing import Any, Callable, Optional
from sim.core_types import Step, SimConfiguration, SimulationEvent, OperationPayload, GeneratorFn
from sim.operations import prepared_processor, prepared_operation, resolve_operation
from sim.util import get_operation_file_params, merge_operation_params


class NestableGenerator:
    parent = None
    prepared_generator: Optional[GeneratorFn] = None
    children: list['NestableGenerator'] = []

    def __init__(self,
                 config: SimConfiguration,
                 generator_declaration: dict,
                 time_point: int,
                 parent: Optional['NestableGenerator'] = None):
        self.parent = parent
        self.generator_type = list(generator_declaration.keys())[0]
        children_tags = generator_declaration[self.generator_type]
        wrappable_operations = []

        for child in children_tags:
            if isinstance(child, dict):
                # Encountered a nested generator.
                if list(child.keys())[0] in ('sequence', 'alternative'):
                    if len(wrappable_operations) > 0:
                        #  Must wrap operations so far under a nested generator of our type.
                        wrapping_generator_declaration = {
                            self.generator_type: wrappable_operations
                        }
                        self.children.append(NestableGenerator(config, wrapping_generator_declaration, time_point, self))
                        wrappable_operations = []
                    self.children.append(NestableGenerator(config, child, time_point, self))
                else:
                    # Encountered an operation.
                    # TODO: case for in-line parameters for operation #211, #217
                    ...
            elif isinstance(child, str):
                parameter_set_choices = config.operation_params.get(child, [{}])
                if len(parameter_set_choices) > 1 and self.generator_type == 'sequence':
                    raise Exception("Alternatives by operation parameters not supported in sequences. Use "
                                    "alternatives clause for operation {} in time point {} or reduce operation parameter "
                                    "set size to 0 or 1.".format(child, time_point))
                wrappable_operations.extend(prepare_parametrized_operations(config, child, time_point))
        if len(wrappable_operations) > 0:
            if len(self.children):
                raise Exception("Unrecoverable fault in NestedGenerator. Having stray unwrapped operations in a nested generator declaration.")
            self.prepared_generator = generator_function(self.generator_type, GENERATOR_LOOKUP, *wrappable_operations)


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


def compose(*generator_series: GeneratorFn) -> Step:
    """
    Generate a simulation Step tree using the given list of generator functions
    :param generator_series: generator functions which produce sequences and branches ('alternatives') of Step function wrappers
    :return: The root node of the generated tree
    """
    root = Step()
    previous = [root]
    for generator in generator_series:
        current = generator(previous)
        previous = current
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


def full_tree_generators(config: SimConfiguration) -> list[NestableGenerator]:
    """
    Creat a list of step generator functions describing a single simulator run.

    :param config: a prepared SimConfiguration object
    :return: a list of prepared generator functions
    """
    generator_series = []

    for time_point in config.time_points:
        generator_declarations = generator_declarations_for_time_point(config.events, time_point)
        for generator_declaration in generator_declarations:
            generator = NestableGenerator(config, generator_declaration, time_point)
            generator_series.append(generator)
    return generator_series


def partial_tree_generators_by_time_point(config: SimConfiguration) -> dict[int, list[NestableGenerator]]:
    """
    Create a dict of NestableGenerators describing keyed by their time_point in the simulation. Used for generating
    partial step trees of the simulation.

    :param config: a prepared SimConfiguration object
    :return: a list of prepared generator functions
    """

    generators_by_time_point = {}

    for time_point in config.time_points:
        generator_series = []
        generator_declarations = generator_declarations_for_time_point(config.events, time_point)
        for generator_declaration in generator_declarations:
            generator = NestableGenerator(config, generator_declaration, time_point)
            generator_series.append(generator)
        generators_by_time_point[time_point] = generator_series
    return generators_by_time_point

