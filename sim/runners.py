from typing import Optional, Any, Callable, List


def evaluate_sequence(payload: Any, *operations: Callable) -> Optional[Any]:
    """
    Compute a single processing result for single data input.

    Execute all given instruction functions, chaining the input_data argument and
    iterative results as arguments to subsequent calls. Abort on any function raising an exception.

    :param payload: argument for the first instruction functions
    :param operations: *arg list of operation functions to execute in order
    :raises Exception: on any instruction function raising, catch and propagate the exception
    :return: return value of the last instruction function
    """
    result = None
    current = payload
    try:
        for func in operations:
            result = func(current)
            current = result
    except Exception as e:
        print("Sequence aborted")
        raise e
    return result


def run_chains_iteratively(payload: Any, chains: List[List[Callable]]):
    iteration_counter = 1
    for chain in chains:
        try:
            print("running chain " + str(iteration_counter))
            iteration_counter = iteration_counter + 1
            result = evaluate_sequence(payload, *chain)

            print(result)
        except Exception as e:
            print(e)
        print("\n")
