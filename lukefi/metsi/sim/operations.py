from typing import Any, Callable, TypeVar

from lukefi.metsi.app.utils import MetsiException


T = TypeVar("T")


def do_nothing(data: T, **kwargs) -> T:
    _ = kwargs
    return data


def prepared_operation(operation_entrypoint: Callable[[T], T], **operation_parameters) -> Callable[[T], T]:
    """prepares an opertion entrypoint function with configuration parameters"""
    return lambda state: operation_entrypoint(state, **operation_parameters)


def simple_processable_chain(operation_tags: list[Callable[[T], T]],
                             operation_params: dict[Callable[[T], T], Any]) -> list[Callable[[T], T]]:
    """Prepare a list of partially applied (parametrized) operation functions based on given declaration of operation
    tags and operation parameters"""
    result: list[Callable[[T], T]] = []
    for tag in operation_tags if operation_tags is not None else []:
        params = operation_params.get(tag, [{}])
        if len(params) > 1:
            raise MetsiException(f"Trying to apply multiple parameter set for preprocessing operation \'{tag}\'. "
                                 "Defining multiple parameter sets is only supported for alternative clause "
                                 "generators.")
        result.append(prepared_operation(tag, **params[0]))
    return result
