from typing import Any, Callable, List, Optional
from sim.core_types import Step, SimulationParams
from sim.operations import prepared_processor
from sim.util import get_or_default, dict_value


def sequence(parents: Optional[List[Step]] = None, *operations: Callable) -> List[Step]:
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


def alternatives(parents: Optional[List[Step]] = None, *operations: Callable) -> List[Step]:
    """
    Generate a branches for an optional list of steps, out of a *args list of given operations
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


def compose(*step_generators: Callable) -> Step:
    """
    Generate a simulation Step tree using the given list of generator functions
    :param step_generators: generator functions which produce sequences and branches of Step function wrappers
    :return: The root node of the generated tree
    """
    root = Step()
    previous = [root]
    for generator in step_generators:
        current = generator(previous)
        previous = current
    return root


def repeat(times: int, *step_generators: Callable) -> List[Callable]:
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


def generator_declarations_for_time_point(simulation_steps: List[dict], time: int) -> List[dict]:
    """
    From simulation_steps, find the step generators declared for the given time point. Upon no match,
    a sequence of a single do_nothing operation is supplanted.

    :param simulation_steps: list of step generator declarations with associated simulation time points
    :param time: point of simulation time for selecting matching generators
    :return: list of generator declarations for the desired point of time
    """
    generator_declarations = []
    for generator_candidate in simulation_steps:
        if time in generator_candidate['time_points']:
            generator_declarations.extend(generator_candidate['generators'])
    return generator_declarations


def generator_function(key, generator_lookup: dict, *operations: Callable) -> Callable[[Any], List[Step]]:
    """Crate a generator function wrapper for function in generator_lookup by the key. Binds the
    argument list of operations with the generator."""
    return lambda payload: generator_lookup[key](payload, *operations)


def full_tree_generators_from_declaration(simulation_declaration: dict, operation_lookup: dict) -> List[Callable]:
    """
    Creat a list of step generator functions describing a single simulator run.

    :param simulation_declaration: a dict matching the simulation declaration structure. See README.
    :param operation_lookup: lookup table binding a declared operation name to a Python function reference
    :return: a list of prepared generator functions
    """

    generator_lookup = {
        'sequence': sequence,
        'alternatives': alternatives,
    }
    generator_series = []
    simulation_params = SimulationParams(**simulation_declaration['simulation_params'])
    simulation_events = get_or_default(dict_value(simulation_declaration, 'simulation_events'), [])
    operation_params = get_or_default(dict_value(simulation_declaration, 'operation_params'), {})
    run_constraints = get_or_default(dict_value(simulation_declaration, 'run_constraints'), {})

    for time_point in simulation_params.simulation_time_series():
        generator_declarations = generator_declarations_for_time_point(simulation_events, time_point)
        for generator_declaration in generator_declarations:
            generator = prepare_step_generator(generator_declaration, generator_lookup, operation_lookup,
                                               operation_params, run_constraints, time_point)
            generator_series.append(generator)
    return generator_series


def prepare_step_generator(generator_declaration, generator_lookup, operation_lookup, operation_params, run_constraints,
                           time_point):
    generator_tag = list(generator_declaration.keys())[0]
    operation_tags = generator_declaration[generator_tag]
    processors = []
    for operation_tag in operation_tags:
        processor = generate_processor(operation_lookup, operation_params, operation_tag, run_constraints, time_point)
        processors.append(processor)
    generator = generator_function(generator_tag, generator_lookup, *processors)
    return generator


def generate_processor(operation_lookup, operation_params, operation_tag, run_constraints, time_point):
    this_operation_params = get_or_default(operation_params.get(operation_tag), {})
    this_run_constraints = get_or_default(run_constraints.get(operation_tag), None)
    result = prepared_processor(
        operation_tag,
        operation_lookup,
        time_point,
        this_run_constraints,
        **this_operation_params)
    return result
