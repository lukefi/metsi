from typing import Optional, Any, Callable


def sequence(*instructions: Callable[[Optional[Any]], Optional[Any]]):
    """
    Execute all parameter callables. Abort if any callable raises an Exception.

    :param instructions: *arg callables to execute in order
    :return: list of result values from all *arg callables in order
    """
    results = []
    try:
        for func in instructions:
            result = func()
            results.append(result)
    except Exception as e:
        print("Sequence aborted")
        raise e
    return results


def split(*instructions: Callable[..., Optional[Any]]):
    """
    Execute all parameter callables. Abort if every callable raises an exception.

    :param instructions: *arg callables to execute in order
    :return: list of result values from all successful *arg callables in order
    """
    results = []
    has_success = False
    for func in instructions:
        try:
            result = func()
            results.append(result)
            has_success = True
        except Exception as e:
            print("Branch aborted")
            print(e)
            results.append(None)
    if has_success is False:
        raise Exception("No branch succeeded")
    return results
