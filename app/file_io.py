import json
import pickle
import jsonpickle
from typing import List, Any

import yaml
from forestdatamodel.model import ForestStand, ReferenceTree


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def read_stands_from_file(file_path: str, input_format: str) -> List[ForestStand]:
    if input_format == "pickle":
        return forest_stands_from_pickle(file_path)
    elif input_format == "json":
        return forest_stands_from_jsonpickle(file_path)
    else:
        raise Exception(f"Unsupported input format '{input_format}'")

def forest_stands_from_pickle(file_path: str) -> List[ForestStand]:
    stands = pickle_reader(file_path)
    return stands

def forest_stands_from_json_file(file_path: str) -> List[ForestStand]:
    # TODO: content validation
    return json.loads(file_contents(file_path),
                      object_hook=lambda d: ReferenceTree(**d) if "tree" in d['identifier'] else ForestStand(**d))


def forest_stands_from_jsonpickle(file_path: str) -> List[ForestStand]:
    stands = jsonpickle.decode(file_contents(file_path))
    return stands

def simulation_declaration_from_yaml_file(file_path: str) -> dict:
    # TODO: content validation
    return yaml.load(file_contents(file_path), Loader=yaml.CLoader)


def pickle_writer(file_path: str, data: Any):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f, protocol=5)


def pickle_reader(file_path: str) -> Any:
    with open(file_path, 'rb') as f:
        return pickle.load(f)
