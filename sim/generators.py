from typing import Any, Callable, Iterable


def instruction_with_options(instruction: Callable, options: Iterable[Any]) -> Iterable[Callable]:
    """
    Curry a function f(X,Y) into a list of functions f(x) with each value of options in order.
    Convenience method for obtaining branch entry points for *alternatives* call.
    :param instruction: function with signature f(X,Y)
    :param options: the values Y
    :return: list of functions with signature f(X), curried with values Y
    """
    return map(lambda option: lambda x: instruction(x, option), options)
