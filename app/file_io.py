import pickle
import jsonpickle
from typing import Any
import yaml


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def read_input_file(file_path: str, input_format: str) -> Any:
    if input_format == "pickle":
        return pickle_reader(file_path)
    elif input_format == "json":
        return json_reader(file_path)
    else:
        raise Exception(f"Unsupported input format '{input_format}'")


def write_result_to_file(result: Any, file_path: str, output_format: str):
    if output_format == "pickle":
        pickle_writer(file_path, result)
    elif output_format == "json":
        json_writer(file_path, result)
    else:
        raise Exception(f"Unsupported output format '{output_format}'")


def simulation_declaration_from_yaml_file(file_path: str) -> dict:
    # TODO: content validation
    return yaml.load(file_contents(file_path), Loader=yaml.CLoader)


def pickle_writer(file_path: str, data: Any):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f, protocol=5)


def pickle_reader(file_path: str) -> Any:
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def json_writer(file_path: str, data: Any):
    jsonpickle.set_encoder_options("json", indent=2)
    with open(file_path, 'w', newline='\n') as f:
        f.write(jsonpickle.encode(data))


def json_reader(file_path: str) -> Any:
    res = jsonpickle.decode(file_contents(file_path))
    return res


