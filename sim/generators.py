from typing import Any, Callable, Iterable, List, Optional
from sim.computation_model import Step


def instruction_with_options(instruction: Callable, options: Iterable[Any]) -> Iterable[Callable]:
    """
    Partially apply options Y to function f(X,Y) to create an iterable of functions f(X), ...
    Convenience method for obtaining branch entry points for *alternatives* call.
    :param instruction: function with signature f(X,Y)
    :param options: the values Y
    :return: list of functions with signature f(X), curried with values Y
    """
    return map(lambda option: lambda x: instruction(x, option), options)


def sequence(parents: Optional[List[Step]] = None, *operations: Callable) -> List[Step]:
    """
    Generate a linear sequence of steps, optionally extending each Step in the given list of Steps with it.
    :param parents: optional
    :param operations:
    :return:
    """
    result = []
    if parents is None or len(parents) is 0:
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
    if parents is None or len(parents) is 0:
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
    for i in range(1, times):
        for generator in step_generators:
            result.append(generator)
    return result
