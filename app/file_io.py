import json
from typing import List
import yaml
from forestdatamodel.model import ForestStand, ReferenceTree


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
