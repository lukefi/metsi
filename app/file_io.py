import argparse
import os
import pickle
from pathlib import Path
import jsonpickle
from typing import Any, Callable
import yaml
from forestdatamodel.formats.ForestBuilder import VMI13Builder, VMI12Builder, ForestCentreBuilder, ForestBuilder
from forestdatamodel.formats.file_io import vmi_file_reader, xml_file_reader, stands_to_csv, csv_to_stands, rsd_rows
from forestdatamodel.model import ForestStand
from sim.core_types import OperationPayload, AggregatedResults


StandReader = Callable[[str], list[ForestStand]]
StandWriter = Callable[[Path, list[ForestStand]], None]
ObjectWriter = Callable[[Path, Any], None]


def prepare_target_directory(path_descriptor: str) -> Path:
    if os.path.exists(path_descriptor):
        if os.path.isdir(path_descriptor) and os.access(path_descriptor, os.W_OK):
            return Path(path_descriptor)
        else:
            raise Exception("Output directory {} not available. Ensure it is a writable and empty, or a non-existing directory.".format(path_descriptor))
    else:
        os.makedirs(path_descriptor)
        return Path(path_descriptor)


def stand_writer(container_format: str) -> StandWriter:
    """Return a serialization file writer function for a list[ForestStand]"""
    if container_format == "pickle":
        return pickle_writer
    elif container_format == "json":
        return json_writer
    elif container_format == "csv":
        return csv_writer
    elif container_format == "rsd":
        return rsd_writer
    else:
        raise Exception(f"Unsupported container format '{container_format}'")


def object_writer(container_format: str) -> ObjectWriter:
    """Return a serialization file writer function for arbitrary data"""
    if container_format == "pickle":
        return pickle_writer
    elif container_format == "json":
        return json_writer
    else:
        raise Exception(f"Unsupported container format '{container_format}'")


def determine_file_path(dir: Path, filename: str) -> Path:
    return Path(dir, filename)


def file_contents(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def fdm_reader(container_format: str) -> StandReader:
    if container_format == "pickle":
        return pickle_reader
    elif container_format == "json":
        return json_reader
    elif container_format == "csv":
        return lambda path: csv_to_stands(path, ';')
    else:
        raise Exception(f"Unsupported container format '{container_format}'")


def external_reader(state_format: str, **builder_flags) -> StandReader:
    if state_format == "vmi13":
        return lambda path: VMI13Builder(builder_flags, vmi_file_reader(path)).build()
    elif state_format == "vmi12":
        return lambda path: VMI12Builder(builder_flags, vmi_file_reader(path)).build()
    elif state_format == "forest_centre":
        return lambda path: ForestCentreBuilder(builder_flags, xml_file_reader(path)).build()


def read_stands_from_file(file_path: str, state_format: str, container_format: str, **builder_flags) -> list[ForestStand]:
    builder_flags = {"reference_trees": False, "strata_origin": "1"} if builder_flags == {} else builder_flags
    if state_format == "fdm":
        return fdm_reader(container_format)(file_path)
    elif state_format in ("vmi13", "vmi12", "forest_centre"):
        return external_reader(state_format, **builder_flags)(file_path)
    else:
        raise Exception(f"Unsupported state format '{state_format}'")


def read_full_simulation_result_input_file(file_path: str, input_format: str) -> dict[str, list[OperationPayload]]:
    if input_format == "pickle":
        return pickle_reader(file_path)
    elif input_format == "json":
        return json_reader(file_path)
    else:
        raise Exception(f"Unsupported input format '{input_format}'")


def write_full_simulation_result_to_file(result: Any, directory: Path, output_format: str):
    override_format = "json" if output_format == "csv" else output_format
    writer = object_writer(override_format)
    filepath = determine_file_path(directory, f"output.{override_format}")
    writer(filepath, result)


def write_stands_to_file(result: list[ForestStand], filepath: Path, state_output_container: str):
    writer = stand_writer(state_output_container)
    writer(filepath, result)


def write_derived_data_to_file(result: AggregatedResults, filepath: Path, derived_data_output_container: str):
    writer = object_writer(derived_data_output_container)
    writer(filepath, result)


def write_post_processing_result_to_file(result: Any, directory: Path, output_format: str):
    override_format = "json" if output_format == "csv" else output_format
    writer = object_writer(override_format)
    filepath = determine_file_path(directory, f"pp_result.{override_format}")
    writer(filepath, result)


def write_full_simulation_result_dirtree(result: dict[str, list[OperationPayload]], app_arguments: argparse.Namespace):
    for stand_id, schedules in result.items():
        for i, schedule in enumerate(schedules):
            if app_arguments.state_output_container is not None:
                schedule_dir = prepare_target_directory(f"{app_arguments.target_directory}/{stand_id}/{i}")
                filepath = determine_file_path(schedule_dir, f"unit_state.{app_arguments.state_output_container}")
                write_stands_to_file([schedule.simulation_state], filepath, app_arguments.state_output_container)
            if app_arguments.derived_data_output_container is not None:
                schedule_dir = prepare_target_directory(f"{app_arguments.target_directory}/{stand_id}/{i}")
                filepath = determine_file_path(schedule_dir, f"derived_data.{app_arguments.derived_data_output_container}")
                write_derived_data_to_file(schedule.aggregated_results, filepath, app_arguments.derived_data_output_container)


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


def rsd_writer(filepath: Path, data: list[ForestStand]):
    with open(filepath, 'w', newline='\n') as file:
        file.writelines('\n'.join(rsd_rows(data)))


def json_reader(file_path: str) -> Any:
    res = jsonpickle.decode(file_contents(file_path))
    return res


