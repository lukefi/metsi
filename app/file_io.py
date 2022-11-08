import argparse
import os
import pickle
from pathlib import Path
import jsonpickle
from typing import Any, Callable
import yaml
from forestdatamodel.formats.ForestBuilder import VMI13Builder, VMI12Builder, ForestCentreBuilder
from forestdatamodel.formats.file_io import vmi_file_reader, xml_file_reader, stands_to_csv, csv_to_stands
from forestdatamodel.model import ForestStand

from sim.core_types import OperationPayload, AggregatedResults


def prepare_target_directory(path_descriptor: str) -> Path:
    if os.path.exists(path_descriptor):
        if os.path.isdir(path_descriptor) and os.access(path_descriptor, os.W_OK):
            return Path(path_descriptor)
        else:
            raise Exception("Output directory {} not available. Ensure it is a writable and empty, or a non-existing directory.".format(path_descriptor))
    else:
        os.makedirs(path_descriptor)
        return Path(path_descriptor)


def get_stands_writer(type: str) -> Callable[[Path, list[ForestStand]], None]:
    if type == "pickle":
        return pickle_writer
    elif type == "json":
        return json_writer
    elif type == "csv":
        return csv_writer
    else:
        raise Exception(f"Unsupported container format '{type}'")


def get_object_writer(type: str) -> Callable[[Path, Any], None]:
    if type == "pickle":
        return pickle_writer
    elif type == "json":
        return json_writer
    else:
        raise Exception(f"Unsupported container format '{type}'")


def determine_file_path(dir: Path, filename: str) -> Path:
    return Path(dir, filename)


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def read_stands_from_file(file_path: str, state_format: str, container_format: str, **builder_flags) -> list[ForestStand]:
    builder_flags = {"reference_trees": False, "strata_origin": "1"} if builder_flags == {} else builder_flags
    if state_format == "fdm":
        if container_format == "pickle":
            return pickle_reader(file_path)
        elif container_format == "json":
            return json_reader(file_path)
        elif container_format == "csv":
            return csv_to_stands(file_path, ';')
        else:
            raise Exception(f"Unsupported container format '{container_format}'")
    elif state_format == "vmi13":
        Builder, read = VMI13Builder, vmi_file_reader
    elif state_format == "vmi12":
        Builder, read = VMI12Builder, vmi_file_reader
    elif state_format == "forest_centre":
        Builder, read = ForestCentreBuilder, xml_file_reader
    else:
        raise Exception(f"Unsupported state format '{state_format}'")
    return Builder(builder_flags, read(file_path)).build()


def read_full_simulation_result_input_file(file_path: str, input_format: str) -> dict[str, list[OperationPayload]]:
    if input_format == "pickle":
        return pickle_reader(file_path)
    elif input_format == "json":
        return json_reader(file_path)
    else:
        raise Exception(f"Unsupported input format '{input_format}'")


def write_preprocessing_result_to_file(result: list[ForestStand], directory: Path, output_format: str):
    writer = get_stands_writer(output_format)
    filepath = determine_file_path(directory, f"preprocessing_result.{output_format}")
    writer(filepath, result)


def write_full_simulation_result_to_file(result: Any, directory: Path, output_format: str):
    override_format = "json" if output_format == "csv" else output_format
    writer = get_object_writer(override_format)
    filepath = determine_file_path(directory, f"output.{override_format}")
    writer(filepath, result)


def write_stands_to_file(result: list[ForestStand], directory: Path, output_format: str):
    writer = get_stands_writer(output_format)
    filepath = determine_file_path(directory, f"unit_state.{output_format}")
    writer(filepath, result)


def write_derived_data_to_file(result: AggregatedResults, directory: Path, output_format: str):
    override_format = "json" if output_format == "csv" else output_format
    writer = get_object_writer(override_format)
    filepath = determine_file_path(directory, f"derived_data.{override_format}")
    writer(filepath, result)


def write_post_processing_result_to_file(result: Any, directory: Path, output_format: str):
    override_format = "json" if output_format == "csv" else output_format
    writer = get_object_writer(override_format)
    filepath = determine_file_path(directory, f"pp_result.{override_format}")
    writer(filepath, result)


def write_full_simulation_result_dirtree(result: dict[str, list[OperationPayload]], app_arguments: argparse.Namespace):
    for stand_id, schedules in result.items():
        for i, schedule in enumerate(schedules):
            schedule_dir = prepare_target_directory(f"{app_arguments.target_directory}/{stand_id}/{i}")
            if app_arguments.state_output_container is not None:
                write_stands_to_file([schedule.simulation_state], schedule_dir, app_arguments.state_output_container)
            if app_arguments.derived_data_output_container is not None:
                write_derived_data_to_file(schedule.aggregated_results, schedule_dir, app_arguments.derived_data_output_container)


def simulation_declaration_from_yaml_file(file_path: str) -> dict:
    # TODO: content validation
    return yaml.load(file_contents(file_path), Loader=yaml.CLoader)


def pickle_writer(filepath: Path, data: Any):
    with open(filepath, 'wb') as f:
        pickle.dump(data, f, protocol=5)


def pickle_reader(file_path: str) -> Any:
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def json_writer(filepath: Path, data: Any):
    jsonpickle.set_encoder_options("json", indent=2)
    with open(filepath, 'w', newline='\n') as f:
        f.write(jsonpickle.encode(data))


def csv_writer(filepath: Path, data: Any):
    with open(filepath, 'w', newline='\n') as file:
        file.writelines('\n'.join(stands_to_csv(data, ';')))


def json_reader(file_path: str) -> Any:
    res = jsonpickle.decode(file_contents(file_path))
    return res


