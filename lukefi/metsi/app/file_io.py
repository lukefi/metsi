import csv
import os
import pickle
import importlib.util
from collections.abc import Iterator, Callable
from pathlib import Path
from typing import Any, Optional
import numpy as np
import jsonpickle
from lukefi.metsi.data.formats.forest_builder import VMI13Builder, VMI12Builder, XMLBuilder, GeoPackageBuilder
from lukefi.metsi.data.formats.io_utils import (
    stands_to_csv_content,
    csv_content_to_stands,
    stands_to_rst_content,
    mela_par_file_content)
from lukefi.metsi.app.app_io import MetsiConfiguration
from lukefi.metsi.app.app_types import ExportableContainer
from lukefi.metsi.domain.forestry_types import SimResults
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.domain.forestry_types import ForestOpPayload, StandList, ForestStand
from lukefi.metsi.data.formats.declarative_conversion import Conversion
from lukefi.metsi.app.utils import MetsiException
from lukefi.metsi.sim.collected_data import CollectedData

StandReader = Callable[[str | Path], StandList]
StandWriter = Callable[[Path, ExportableContainer[PossiblyLayered[ForestStand]]], None]
ObjectLike = StandList | SimResults | CollectedData
ObjectWriter = Callable[[Path, ObjectLike], None]

# io_utils?
def prepare_target_directory(path_descriptor: str) -> Path:
    """
    Sanity check a given directory path. Existing directory must be accessible for writing. Raise exception if directory
    is not usable. Create the directory if not existing.
    necessary.

    :param path_descriptor: relative directory path
    :return: Path instance for directory
    """
    if os.path.exists(path_descriptor):
        if os.path.isdir(path_descriptor) and os.access(path_descriptor, os.W_OK):
            return Path(path_descriptor)
        raise MetsiException(
            f"Output directory {path_descriptor} not available. Ensure it is a writable and empty, "
            "or a non-existing directory.")

    os.makedirs(path_descriptor)
    return Path(path_descriptor)

# solve FileWriter - interface
def stand_writer(container_format: str) -> StandWriter:
    """Return a serialization file writer function for a ForestDataPackage"""
    if container_format == "pickle":
        return pickle_writer
    if container_format == "json":
        return json_writer
    if container_format == "csv":
        return csv_writer
    if container_format == "rst":
        return rst_writer
    if container_format == "npy":
        return npy_writer
    if container_format == "npz":
        return npz_writer
    raise MetsiException(f"Unsupported container format '{container_format}'")


# entry of FileWriter
def write_stands_to_file(
        result: ExportableContainer[PossiblyLayered[ForestStand]], filepath: Path, state_output_container: str):
    """Resolve a writer function for ForestStands matching the given state_output_container. Invokes write."""
    writer = stand_writer(state_output_container)
    writer(filepath, result)

# solve ObjectWriter
def object_writer(container_format: str) -> ObjectWriter:
    """Return a serialization file writer function for arbitrary data"""
    if container_format == "pickle":
        return pickle_writer
    if container_format == "json":
        return json_writer
    raise MetsiException(f"Unsupported container format '{container_format}'")

# io_utils
def determine_file_path(dir_: str | Path, filename: str) -> Path:
    return Path(dir_, filename)

# io_utils
def file_contents(file_path: str | Path) -> str:
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

# solve FdmReader
def fdm_reader(container_format: str) -> StandReader:
    """Resolve a reader function for FDM data containers"""
    if container_format == "pickle":
        return pickle_reader
    if container_format == "json":
        return json_reader
    if container_format == "csv":
        return lambda path: csv_content_to_stands(csv_file_reader(path))
    raise MetsiException(f"Unsupported container format '{container_format}'")

# solve ObjectReader
def object_reader(container_format: str) -> Any:
    if container_format == "pickle":
        return pickle_reader
    if container_format == "json":
        return json_reader
    raise MetsiException(f"Unsupported container format '{container_format}'")

# SourceDataReaders
def external_reader(state_format: str, conversions, **builder_flags) -> StandReader:
    """Resolve and prepare a reader function for non-FDM data formats"""
    if state_format == "vmi13":
        return lambda path: VMI13Builder(builder_flags, conversions.get('vmi13', {}), vmi_file_reader(path)).build()
    if state_format == "vmi12":
        return lambda path: VMI12Builder(builder_flags, conversions.get('vmi12', {}), vmi_file_reader(path)).build()
    if state_format == "xml":
        return lambda path: XMLBuilder(builder_flags, conversions.get('xml', {}), xml_file_reader(path)).build()
    if state_format == "gpkg":
        return lambda path: GeoPackageBuilder(builder_flags, conversions.get('gpkg', {}), str(path)).build()
    raise MetsiException(f"Unsupported state format '{state_format}'")

# source data main entry function
def read_stands_from_file(app_config: MetsiConfiguration, conversions: dict[str, Conversion]) -> StandList:
    """
    Read a list of ForestStands from given file with given configuration. Directly reads FDM format data. Utilizes
    FDM ForestBuilder utilities to transform VMI12, VMI13 or Forest Centre data into FDM ForestStand format.

    :param app_config: Mela2Configuration
    :return: list of ForestStands as computational units for simulation
    """
    if app_config.state_format == "fdm":
        return fdm_reader(app_config.state_input_container.value)(app_config.input_path)
    if app_config.state_format in ("vmi13", "vmi12", "xml", "gpkg"):
        return external_reader(
            app_config.state_format.value,
            conversions,
            strata=app_config.strata,
            measured_trees=app_config.measured_trees,
            strata_origin=app_config.strata_origin)(app_config.input_path)
    raise MetsiException(f"Unsupported state format '{app_config.state_format}'")

# io_util?
def scan_dir_for_file(dirpath: Path, basename: str, suffixes: list[str]) -> Optional[tuple[Path, str]]:
    """
    From given directory path, find the filename for given basename with list of possible file suffixes.
    Raises Exception if directory path is not a directory.
    :returns a pair with full filename and matching suffix
    """
    if not os.path.isdir(dirpath):
        raise MetsiException(f"Given input path {dirpath} is not a directory.")
    _, _, files = next(os.walk(dirpath))
    filenames_with_suffix = list(map(lambda suffix: (f"{basename}.{suffix}", suffix), suffixes))
    for filename, suffix in filenames_with_suffix:
        if filename in files:
            return Path(dirpath, filename), suffix
    return None

# io_util?
def parse_file_or_default(file: Path, reader: Callable[[Path], Any], default=None) -> Optional[Any]:
    """Deserialize given file with given reader function or return default"""
    if os.path.exists(file):
        return reader(file)
    return default

# SimResultReader utility - scans schedules from files
def read_schedule_payload_from_directory(schedule_path: Path) -> ForestOpPayload:
    """
    Create an OperationPayload from a directory which optionally contains usable unit_state and derived_data files.
    Utilizes a scanner function to resolve the files with known container formats. Files may not exist.

    :param schedule_path: Path for a schedule directory
    :return: OperationPayload with computational_unit and collected_data if found
    """
    scan_result = scan_dir_for_file(schedule_path, "unit_state", ["csv", "json", "pickle"])
    # unit_state_file, input_container = scan_dir_for_file(schedule_path, "unit_state", ["csv", "json", "pickle"])
    if scan_result is not None:
        unit_state_file, input_container = scan_result
    else:
        unit_state_file = None
        input_container = None

    scan_result = scan_dir_for_file(schedule_path, "derived_data", ["json", "pickle"])
    # derived_data_file, derived_data_container = scan_dir_for_file(schedule_path, "derived_data", ["json", "pickle"])
    if scan_result is not None:
        derived_data_file, derived_data_container = scan_result
    else:
        derived_data_file = None
        derived_data_container = None

    stands = [] if unit_state_file is None or input_container is None else parse_file_or_default(
        unit_state_file, fdm_reader(input_container), [])
    derived_data = None if derived_data_file is None or derived_data_container is None else parse_file_or_default(
        derived_data_file, object_reader(derived_data_container))

    return ForestOpPayload(
        computational_unit=None if stands == [] or stands is None else stands[0],
        collected_data=derived_data,
        operation_history=[]
    )

# io_util?
def get_subdirectory_names(path: str | Path) -> list[str]:
    if not os.path.isdir(path):
        raise MetsiException(f"Given input path {path} is not a directory.")
    _, dirs, _ = next(os.walk(path))
    return dirs

# SimResult entry function
def read_full_simulation_result_dirtree(source_path: str | Path) -> SimResults:
    """
    Read simulation results from a given source directory, packing them into the simulation results dict structure.
    Utilizes a directory scanner function to find unit_state and derived_data files for known possible container
    formats.

    :param source_path: Path for simulation results
    :return: simulation results dict structure
    """
    def schedulepaths_for_stand(stand_path: Path) -> Iterator[Path]:
        schedules = get_subdirectory_names(stand_path)
        return map(lambda schedule: Path(stand_path, schedule), schedules)
    result = {}
    stand_identifiers = get_subdirectory_names(source_path)
    stands_to_schedules = map(lambda stand_id: (
        stand_id, schedulepaths_for_stand(Path(source_path, stand_id))), stand_identifiers)
    for stand_id, schedulepaths in stands_to_schedules:
        payloads = list(map(read_schedule_payload_from_directory, schedulepaths))
        result[stand_id] = payloads
    return result

# CollectedResults writer, done when SimResults are written.
# - can be seen as indivudual entry for writing CollectedResults
def write_derived_data_to_file(result: CollectedData, filepath: Path, derived_data_output_container: str):
    """
    Resolve a writer function for AggregatedResults matching the given derived_data_output_container.
    Invokes write.
    """
    writer = object_writer(derived_data_output_container)
    writer(filepath, result)

# SimResult writer entry
def write_full_simulation_result_dirtree(result: SimResults, app_arguments: MetsiConfiguration):
    """
    Unwraps the given simulation result structure into computational units and further into produced schedules.
    Writes these as a matching directory structure, splitting OperationPayloads into unit_state and derived_data files.
    Details for output directory, unit state container format and derived data container format are extracted from
    given app_arguments structure.

    :param result: the simulation results structure
    :param app_arguments: application run configuration
    :return: None
    """
    for stand_id, schedules in result.items():
        for i, schedule in enumerate(schedules):
            if app_arguments.state_output_container is not None:
                schedule_dir = prepare_target_directory(f"{app_arguments.target_directory}/{stand_id}/{i}")
                filepath = determine_file_path(schedule_dir, f"sim_result.{app_arguments.state_output_container.value}")
                write_stands_to_file(ExportableContainer([schedule.computational_unit], None),
                                     filepath,
                                     app_arguments.state_output_container.value)
            if app_arguments.derived_data_output_container is not None:
                schedule_dir = prepare_target_directory(f"{app_arguments.target_directory}/{stand_id}/{i}")
                filepath = determine_file_path(schedule_dir, app_arguments.derived_data_output_container)
                write_derived_data_to_file(schedule.collected_data, filepath,
                                           app_arguments.derived_data_output_container)


def read_control_module(control_path: str, control: str = "control_structure") -> dict[str, Any]:
    config_path = Path(control_path).resolve()  # Ensure absolute path
    module_name = config_path.stem  # Extract filename without extension

    spec = importlib.util.spec_from_file_location(module_name, str(control_path))
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, control):  # Check if variable exists
            return getattr(module, control)
        raise AttributeError(f"Variable '{control}' not found in {config_path}")
    raise ImportError(f"Could not load control module from {config_path}")


##### FileWriters start #####
def pickle_writer(filepath: Path, container: ObjectLike | ExportableContainer):
    outputtable = container.export_objects if isinstance(container, ExportableContainer) else container
    with open(filepath, 'wb') as f:
        pickle.dump(outputtable, f, protocol=5)


def json_writer(filepath: Path, container: ObjectLike | ExportableContainer):
    outputtable = container.export_objects if isinstance(container, ExportableContainer) else container
    jsonpickle.set_encoder_options("json", indent=2)
    with open(filepath, 'w', newline='\n', encoding="utf-8") as f:
        f.write(str(jsonpickle.encode(outputtable)))

# generic writer
def row_writer(filepath: Path, rows: list[str]):
    with open(filepath, 'a', newline='\n', encoding="utf-8") as file:
        for row in rows:
            file.write(row)
            file.write('\n')


def csv_writer(filepath: Path, container: ExportableContainer[PossiblyLayered[ForestStand]]):
    row_writer(filepath, stands_to_csv_content(container, ';'))


def rst_writer(filepath: Path, container: ExportableContainer[PossiblyLayered[ForestStand]]):
    rows = stands_to_rst_content(container)
    row_writer(filepath, rows)
    if container.additional_vars is not None:
        par_writer(filepath, container.additional_vars)

def npy_writer(filepath: Path, container: ExportableContainer):
    stands = container.export_objects
    np.save(filepath, allow_pickle=True, arr=np.array(stands, dtype=object))


def npz_writer(filepath: Path, container: ExportableContainer):
    stands = container.export_objects
    np.savez(filepath, allow_pickle=True, *[np.array(stand) for stand in stands])


def par_writer(filepath: Path, var_names: list[str]):
    def to_par_filepath(filepath: Path):
        dir_parts = list(filepath.parts)[0:-1]
        return determine_file_path(os.path.join(*dir_parts), 'c-variables.par')
    row_writer(to_par_filepath(filepath), mela_par_file_content(var_names))

##### SourceFileReaders start #####
def vmi_file_reader(file: str | Path) -> list[str]:
    with open(file, 'r', encoding='utf-8') as input_file:
        return input_file.readlines()


def xml_file_reader(file: str | Path) -> str:
    with open(file, 'r', encoding='utf-8') as input_file:
        return input_file.read()


def csv_file_reader(file: str | Path) -> list[list[str]]:
    with open(file, 'r', encoding='utf-8') as input_file:
        return list(csv.reader(input_file, delimiter=';'))

## ObjectFileReaders start ##
def json_reader(file_path: str | Path) -> StandList:
    return jsonpickle.decode(file_contents(file_path)) # type: ignore


def pickle_reader(file_path: str | Path) -> StandList:
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def npy_file_reader(file_path: str | Path) -> np.ndarray:
    with open(file_path, 'rb') as f:
        return np.load(f, allow_pickle=True)

def npz_file_reader(file_path: str | Path):
    with np.load(file_path, allow_pickle=True) as data:
        retval = []
        for v in data.values():
            retval.append(v)
    return retval
