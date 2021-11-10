from typing import Any, Callable, Iterable


def instruction_with_options(instruction: Callable, options: Iterable[Any]) -> Iterable[Callable]:
    """
    Partially apply options Y to function f(X,Y) to create an iterable of functions f(X), ...
    Convenience method for obtaining branch entry points for *alternatives* call.
    :param instruction: function with signature f(X,Y)
    :param options: the values Y
    :return: list of functions with signature f(X), curried with values Y
    """
    return map(lambda option: lambda x: instruction(x, option), options)
