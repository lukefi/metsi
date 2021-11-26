from typing import Any, Callable, Iterable, List, Optional
from computation_model import Step


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
