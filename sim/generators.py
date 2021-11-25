from typing import Any, Callable, Iterable, List
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


def sequence(parents: List[Step] = None, *operations: Callable) -> List[Step]:
    result = []
    if parents is None or len(parents) is 0:
        raise Exception("Unable to generate Step sequence without attachment points")
    for root_step in parents:
        previous_step = root_step
        for operation in operations:
            current_step = Step(operation, previous_step)
            previous_step.add_branch(current_step)
            previous_step = current_step
        result.append(previous_step)
    return result
