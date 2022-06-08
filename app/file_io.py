import json
import pickle
from typing import List, Any, Callable
import yaml
from forestdatamodel import ForestStand, ReferenceTree


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def forest_stands_from_json_file(file_path: str) -> List[ForestStand]:
    # TODO: content validation
    return json.loads(file_contents(file_path),
                      object_hook=lambda d: ReferenceTree(**d) if "tree" in d['identifier'] else ForestStand(**d))


def simulation_declaration_from_yaml_file(file_path: str) -> dict:
    # TODO: content validation
    return yaml.load(file_contents(file_path), Loader=yaml.CLoader)


def pickle_writer(file_path: str, data: Any):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f, protocol=5)


def pickle_reader(file_path: str) -> Any:
    with open(file_path, 'rb') as f:
        return pickle.load(f)
