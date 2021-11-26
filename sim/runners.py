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


def evaluate_alternatives(input_data: Optional[Any], *instructions: Callable[..., Optional[Any]]) -> List[Optional[Any]]:
    """
    Compute alternative processing results for single data input.

    Execute all given instruction functions with
    input_data and return a list of their results in order. Abort if every callable raises an exception.

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


def follow(input_datas: List[Optional[Any]],
           instruction: Callable[[Optional[Any]], Optional[Any]]) -> List[Optional[Any]]:
    """
    Compute processing results for multiple data inputs using a single instruction function.

    Execute argument instruction function separately for each element in input_datas. Return the results of each
    call arrayed into a list.

    :param input_datas: list of arguments for instruction functions
    :param instruction: a function to be called for each input data item
    :return: list of result values or None from all successful *arg callables in order
    """
    results = []
    has_success = False
    for input_data in input_datas:
        try:
            result = instruction(input_data)
            results.append(result)
            has_success = True
        except Exception as e:
            print("A branch failed")
            print(e)
            results.append(None)
    if has_success is False:
        raise Exception("All branches failed to produce results")
    return results


def reduce(input_datas: List[Optional[Any]],
           reducer: Callable[[List[Optional[Any]]], Optional[Any]]) -> Optional[Any]:
    """
    Obtain a single result out of multiple data inputs, using the given instruction as a reducer.

    Execute argument instruction function to

    :param input_datas:
    :param reducer: function which should return a single item based on a list of items of same type
    :return:
    """
    try:
        result = reducer(input_datas)
        return result
    except Exception as e:
        print("Reduction of results failed")
        print(e)
        raise e
