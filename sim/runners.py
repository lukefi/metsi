from typing import Optional, Any, Callable, List


def sequence(input_data: Optional[Any], *instructions: Callable[[Optional[Any]], Optional[Any]]) -> Optional[Any]:
    """
    Execute all given instruction functions, chaining the input_data argument and iterative results as arguments to
    subsequent calls. Abort on any function raising an exception.

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


def split(input_data: Optional[Any], *instructions: Callable[..., Optional[Any]]) -> List[Optional[Any]]:
    """
    Execute all given instruction functions with input_data and return a list of their results in order. Abort if every
    callable raises an exception.

    :param input_data: arguments for instruction functions
    :param instructions: list of functions to execute in order
    :raises Exception: on every instruction function failing
    :return: list of result values or None from all successful *arg callables in order
    """
    results = []
    has_success = False
    for func in instructions:
        try:
            result = func(input_data)
            results.append(result)
            has_success = True
        except Exception as e:
            print("Generating a possibility aborted")
            print(e)
            results.append(None)
    if has_success is False:
        raise Exception("Unable to generate any usable possibilities")
    return results
