import os
from typing import Optional, Any
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.sim.event import Treatment


def get_or_default(maybe_value: Optional[Any], default: Any) -> Any:
    return default if maybe_value is None else maybe_value


def get_treatment_file_params(treatment: Treatment) -> dict:
    """
    Checks whether the given parameter file(s) exist and returns the paths as a dict.
    This check ensures that the simulator will not crash later on when it tries to read the files.
    """
    result = {}

    for name, path in treatment.file_parameters.items():
        file_exists = os.path.isfile(path)
        if file_exists:
            result[name] = path
        else:
            raise FileNotFoundError(f"file {path} defined in operation_file_params was not found")
    return result


def merge_operation_params(operation_params: dict, operation_file_params: dict) -> dict:
    """
    Attempts to join the two dicts supplied as arguments. Will throw an exception if the dicts share one or more
    common keys. This is to prevent overwriting a parameter with another.
    """
    common_keys = operation_params.keys() & operation_file_params.keys()
    if common_keys:
        raise MetsiException(
            f"parameter(s) {common_keys} were defined both in 'operation_param' and 'operation_file_param' sections "
            "in control.py. Please change the name of one of them.")
    return operation_params | operation_file_params  # pipe is the merge operator
