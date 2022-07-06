from typing import Optional, Any, Dict

def get_or_default(maybe_value: Optional[Any], default: Any) -> Any:
    return default if maybe_value is None else maybe_value


def dict_value(source: dict, key: str) -> Optional[Any]:
    try:
        return source[key]
    except:
        return None

def read_operation_file_params(opreation_tag: str, operation_file_params: dict) -> Dict:
    result = {}
    operation_param_file_paths = get_or_default(operation_file_params.get(opreation_tag), {})

    for name, path in operation_param_file_paths.items():
        try:
            with open(path, 'r', encoding="utf-8") as f:
                result[name] = f.read()
        except FileNotFoundError as e:
            print(f"file {path} defined in operation_file_params was not found")
            raise e
    return result

def merge_operation_params(operation_params: dict, operation_file_params: dict) -> Dict:
    """Attempts to join the two dicts supplied as arguments. Will throw an exception if the dicts share one or more common keys. This is to prevent overwriting an a parameter with another."""
    common_keys = operation_params.keys() & operation_file_params.keys()
    if common_keys:
        raise Exception(f"parameter(s) {common_keys} were defined both in 'operation_param' and 'operation_file_param' sections in control.yaml. Please change the name of one of them.")
    else:
        return operation_params | operation_file_params # pipe  is the merge operator