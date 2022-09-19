from typing import Any, Callable, List, Optional, Dict
from sim.core_types import Step, SimulationParams
from sim.operations import prepared_processor, prepared_operation, resolve_operation
from sim.util import get_or_default, dict_value, read_operation_file_params, merge_operation_params


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


def compose(*generator_series: Callable) -> Step:
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


def simple_processable_chain(operation_tags: List[str], operation_params: dict, operation_lookup: dict) -> List[
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


def generator_declarations_for_time_point(simulation_events: List[dict], time: int) -> List[dict]:
    """
    From simulation_steps, find the step generators declared for the given time point. Upon no match,
    a sequence of a single do_nothing operation is supplanted.

    :param simulation_steps: list of step generator declarations with associated simulation time points
    :param time: point of simulation time for selecting matching generators
    :return: list of generator declarations for the desired point of time
    """
    generator_declarations = []
    for generator_candidate in simulation_events:
        if time in generator_candidate['time_points']:
            generator_declarations.extend(generator_candidate['generators'])
    return generator_declarations


def generator_function(key, generator_lookup: dict, *processors: Callable) -> Callable[[Any], List[Step]]:
    """Crate a generator function wrapper for function in generator_lookup by the key. Binds the
    argument list of processors with the generator."""
    return lambda parent_steps: generator_lookup[key](parent_steps, *processors)


def get_configuration_from_simulation_declaration(simulation_declaration):
    simulation_params = SimulationParams(**simulation_declaration['simulation_params'])
    simulation_events = get_or_default(dict_value(simulation_declaration, 'simulation_events'), [])
    operation_params = get_or_default(dict_value(simulation_declaration, 'operation_params'), {})
    operation_file_params = get_or_default(dict_value(simulation_declaration, 'operation_file_params'), {})
    run_constraints = get_or_default(dict_value(simulation_declaration, 'run_constraints'), {})
    return simulation_params,simulation_events,operation_params,operation_file_params,run_constraints


def prepare_step_generator(generator_declaration, generator_lookup, operation_lookup, operation_params, operation_file_params, run_constraints,
                           time_point):
    """Return a prepared Step generator function based on simulation declaration and operation details. Operations
    with multiple parameter sets are expanded within their alternatives generator block. Operations with multiple
    parameter sets within a sequence generator block throw an Exception."""
    generator_tag = list(generator_declaration.keys())[0]
    operation_tags = generator_declaration[generator_tag]
    processors = []
    for operation_tag in operation_tags:
        parameter_set_choices = get_or_default(operation_params.get(operation_tag), [{}])
        operation_run_constraints = get_or_default(run_constraints.get(operation_tag), None)
        this_operation_file_params = read_operation_file_params(operation_tag, operation_file_params)
        if len(parameter_set_choices) > 1 and generator_tag == 'sequence':
            raise Exception("Alternatives by operation parameters not supported in sequences. Use "
                            "alternatives clause for operation {} in time point {} or reduce operation parameter "
                            "set size to 0 or 1.".format(operation_tag, time_point))
        for parameter_set in parameter_set_choices:
            combined_params = merge_operation_params(parameter_set, this_operation_file_params)
            processor = prepared_processor(
                operation_tag,
                operation_lookup,
                time_point,
                operation_run_constraints,
                **combined_params)
            processors.append(processor)
    generator = generator_function(generator_tag, generator_lookup, *processors)
    return generator


def full_tree_generators(simulation_declaration: dict, operation_lookup: dict) -> List[Callable]:
    """
    Creat a list of step generator functions describing a single simulator run.

    :param simulation_declaration: a dict matching the simulation declaration structure. See README.
    :param operation_lookup: lookup table binding a declared operation name to a Python function reference
    :return: a list of prepared generator functions
    """
    generator_series = []

    simulation_params, simulation_events, operation_params, operation_file_params, run_constraints = get_configuration_from_simulation_declaration(simulation_declaration)

    for time_point in simulation_params.simulation_time_series():
        generator_declarations = generator_declarations_for_time_point(simulation_events, time_point)
        for generator_declaration in generator_declarations:
            generator = prepare_step_generator(generator_declaration, GENERATOR_LOOKUP, operation_lookup,
                                               operation_params, operation_file_params, run_constraints, time_point)
            generator_series.append(generator)
    return generator_series


def partial_tree_generators_by_time_point(simulation_declaration: dict, operation_lookup: dict) -> Dict[
    int, List[Callable]]:
    """
    Create a dict of step generator functions describing keyed by their time_point in the simulation. Used for generating
    partial step trees of the simulation.

    :param simulation_declaration: a dict matching the simulation declaration structure. See README.
    :param operation_lookup: lookup table binding a declared operation name to a Python function reference
    :return: a list of prepared generator functions
    """

    generators_by_time_point = {}

    simulation_params, simulation_events, operation_params, operation_file_params, run_constraints = get_configuration_from_simulation_declaration(simulation_declaration)

    for time_point in simulation_params.simulation_time_series():
        generator_series = []
        generator_declarations = generator_declarations_for_time_point(simulation_events, time_point)
        for generator_declaration in generator_declarations:
            generator = prepare_step_generator(generator_declaration, GENERATOR_LOOKUP, operation_lookup,
                                               operation_params, operation_file_params, run_constraints, time_point)
            generator_series.append(generator)
        generators_by_time_point[time_point] = generator_series
    return generators_by_time_point

