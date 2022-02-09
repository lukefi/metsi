from typing import Optional, Any, Callable, List


def evaluate_sequence(input_data: Optional[Any], *instructions: Callable[[Optional[Any]], Optional[Any]]) -> Optional[Any]:
    """
    Compute a single processing result for single data input.

    Execute all given instruction functions, chaining the input_data argument and
    iterative results as arguments to subsequent calls. Abort on any function raising an exception.

    :param input_data: argument for the first instruction functions
    :param instructions: *arg list of instruction functions to execute in order
    :raises Exception: on any instruction function raising, catch and propagate the exception
    :return: return value of the last instruction function
    """
    result = None
    current = input_data
    try:
        for func in instructions:
            result = func(current)
            current = result
    except Exception as e:
        print("Sequence aborted")
        raise e
    return result
