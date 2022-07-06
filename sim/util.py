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

def merge_operation_params(operation_params: dict, this_operation_file_params: dict) -> Dict:
    try:
        return join_two_dicts_no_overwrite(operation_params, this_operation_file_params)
    except Exception as e:
        print(f"parameter(s) {e.args[0]} were defined both in 'operation_param' and 'operation_file_param' sections in control.yaml. Please change the name of one of them.")

def join_two_dicts_no_overwrite(dict1: dict, dict2: dict) -> Dict:
    """Attempts to join :dict1: and :dict2:, but if the dictionaries contain any shared keys, Exception will be raised to avoid overwriting a key."""
    common_keys = dict1.keys() & dict2.keys()
    if common_keys:
        raise Exception(common_keys)
    else:
        return dict1 | dict2 # pipe  is the merge operator