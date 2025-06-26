import os
import sys
import copy
import shutil
from pathlib import Path
# TODO: find out what triggers FutureWarning behaviour in numpy
import warnings
import traceback

warnings.simplefilter(action='ignore', category=FutureWarning)

from lukefi.metsi.app.preprocessor import (
    preprocess_stands,
    slice_stands_by_percentage, 
    slice_stands_by_size
    )

from lukefi.metsi.sim.core_types import OperationPayload
from lukefi.metsi.app.enum import FormationStrategy, EvaluationStrategy
from lukefi.metsi.app.app_io import parse_cli_arguments, MetsiConfiguration, generate_application_configuration, RunMode
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.app.export import export_files, export_preprocessed
from lukefi.metsi.app.file_io import prepare_target_directory, read_stands_from_file, \
    read_full_simulation_result_dirtree, write_full_simulation_result_dirtree, read_control_module, \
    read_schedule_payload_from_directory, pickle_reader
from lukefi.metsi.app.post_processing import post_process_alternatives
from lukefi.metsi.app.simulator import simulate_alternatives
from lukefi.metsi.app.console_logging import print_logline
from lukefi.metsi.app.app_types import ForestOpPayload
from lukefi.metsi.data.layered_model import LayeredObject
from lukefi.metsi.domain.sim_ops import *
from lukefi.metsi.domain.pre_ops import *

def preprocess(config: MetsiConfiguration, control: dict, stands: StandList) -> StandList:
    print_logline("Preprocessing...")
    result = preprocess_stands(stands, control)
    return result


def simulate(config: MetsiConfiguration, control: dict, stands: StandList) -> SimResults:
    print_logline("Simulating alternatives...")
    result = simulate_alternatives(config, control, stands)
    if config.state_output_container is not None or config.derived_data_output_container is not None:
        
        schedules_path = os.path.join(config.target_directory, "schedules")
        if os.path.exists(schedules_path) and os.path.isdir(schedules_path):
            print_logline(f"Cleaning previous schedules at '{schedules_path}'")
            shutil.rmtree(schedules_path)

        print_logline(f"Writing simulation results to '{config.target_directory}'")
        write_full_simulation_result_dirtree(result, config)
    return result


def post_process(config: MetsiConfiguration, control: dict, data: SimResults) -> SimResults:
    print_logline("Post-processing alternatives...")
    result = post_process_alternatives(config, control['post_processing'], data)
    if config.state_output_container is not None or config.derived_data_output_container is not None:
        print_logline(f"Writing post-processing results to '{config.target_directory}'")
        write_full_simulation_result_dirtree(result, config)
    return result


def export(config: MetsiConfiguration, control: dict, data: SimResults) -> None:
    print_logline("Exporting simulation results...")
    if control['export']:
        export_files(config, control['export'], data)


def export_prepro(config: MetsiConfiguration, control: dict, data: StandList) -> None:
    print_logline("Exporting preprocessing results...")
    if control.get('export_prepro', None):
        export_preprocessed(config.target_directory, control['export_prepro'], data)
    else:
        print_logline(f"Declaration for 'export_prerocessed' not found from control.")
        print_logline(f"Skipping export of preprocessing results.")
    return data # returned as is just for workflow reasons

mode_runners = {
    RunMode.PREPROCESS: preprocess,
    RunMode.EXPORT_PREPRO: export_prepro,
    RunMode.SIMULATE: simulate,
    RunMode.POSTPROCESS: post_process,
    RunMode.EXPORT: export
}

def replay_schedule(payload: ForestOpPayload) -> ForestOpPayload:
    """
    Given a loaded schedule payload, step through its recorded operation_history
    ([(time_point, op_name, params), …]) and re-apply each op in turn.
    """
    if payload.collected_data is None:
        raise RuntimeError("BUG: payload.collected_data is None before replaying — check deserialization")



    # if your OperationPayload needs layering exactly as in simulate…
    overlaid = LayeredObject(payload.computational_unit)
    payload.computational_unit = overlaid

    for (t, op_name, params) in payload.operation_history:
        # Update time if collected_data is available
        if payload.collected_data is not None:
            payload.collected_data.current_time_point = t

        # Resolve operation function
        if callable(op_name):
            op_fn = op_name
        else:
            op_fn = globals().get(op_name)
        if op_fn is None:
            name = getattr(op_name, "__name__", op_name)
            raise RuntimeError(f"Cannot find operation '{name}' to replay")

        # Run operation in legacy mode
        result = op_fn((payload.computational_unit, payload.collected_data), **params)

        if isinstance(result, tuple) and len(result) == 2:
            new_stand, maybe_new_collected_data = result

            # Only update collected_data if the op returned a non-None one
            new_collected_data = (
                maybe_new_collected_data if maybe_new_collected_data is not None
                else payload.collected_data
            )

            # Rebuild payload
            payload = OperationPayload(
                computational_unit=new_stand,
                collected_data=new_collected_data,
                operation_history=payload.operation_history
            )
        else:
            raise RuntimeError(f"Operation '{op_name}' returned unexpected result: {result}")

    return payload

def main() -> int:
    cli_arguments = parse_cli_arguments(sys.argv[1:])
    resimulation_target   = cli_arguments.pop('resimulate', None)

    control_file = MetsiConfiguration.control_file if cli_arguments["control_file"] is None else cli_arguments['control_file']
    try:
        control_structure = read_control_module(control_file)
    except IOError:
        print(f"Application control file path '{control_file}' can not be read. Aborting....")
        return 1
    try:
        app_config = generate_application_configuration( {**cli_arguments, **control_structure['app_configuration']} )
        prepare_target_directory(app_config.target_directory)
        print_logline("Reading input...")

        #in case of resimulation..
        if resimulation_target:

            resim_path = Path(resimulation_target)
            '''
            payload = read_schedule_payload_from_directory(resim_path)

            print_logline(f"Resimulating {resimulation_target} using control file: {control_file}")
            resim_result = simulate_alternatives(app_config, control_structure, [payload.computational_unit])
            '''
            # 1) load the last payload (unit_state, derived_data, operation_history)
            payload = read_schedule_payload_from_directory(resim_path)
            print_logline(f"Replaying schedule only for {resimulation_target} (no control file)…")

            
            payload.collected_data.operation_results.clear()
            # 2) replay exactly the same operations on that payload
            new_payload = replay_schedule(payload)

            # 3) wrap into the usual results dict and dump it
            resim_result = { payload.computational_unit.identifier: [ new_payload ] }
 
            original_collectives = payload.collected_data.operation_results.get('report_collectives', {})
            
            for schedules in resim_result.values():
                for s in schedules:
                    # ensure the old collectives are present for j_xda
                    s.collected_data.operation_results.setdefault('report_collectives', {}) \
                                        .update(original_collectives)
            
            write_full_simulation_result_dirtree(resim_result, app_config)

            # Post-process
            if 'post_processing' in control_structure:
                resim_result = post_process(app_config, control_structure, resim_result)

            # Export
            if 'export' in control_structure:
                export(app_config, control_structure, resim_result)

            print_logline("Resimulation complete; exiting.")
            return 0
        
        elif app_config.run_modes[0] in [RunMode.PREPROCESS, RunMode.SIMULATE]:
            # 1) read full stand list
            full_stands = read_stands_from_file(app_config, control_structure.get('conversions', {}))

            # 2) split it if slice_* parameters are given
            pct = control_structure.get('slice_percentage')
            sz  = control_structure.get('slice_size')
            if pct is not None:
                stand_sublists = slice_stands_by_percentage(full_stands, pct)
            elif sz is not None:
                stand_sublists = slice_stands_by_size(full_stands, sz)
            else:
                stand_sublists = [full_stands]

            input_data = stand_sublists

        elif app_config.run_modes[0] in [RunMode.POSTPROCESS, RunMode.EXPORT]:
            input_data = read_full_simulation_result_dirtree(app_config.input_path)
        else:
            raise Exception("Can not determine input data for unknown run mode")
    except Exception as e:
        traceback.print_exc()
        print("Aborting run...")
        return 1
    
    # now run each slice in turn
    for slice_idx, stands in enumerate(input_data):
        # -- optional slice folder (disabled for now) --
        # slice_target = os.path.join(app_config.target_directory, f"slice_{slice_idx+1}")
        # prepare_target_directory(slice_target)

        # use original directory instead (to overwrite for now)
        prepare_target_directory(app_config.target_directory)

        # clone config so we don’t stomp on the original
        cfg = copy.copy(app_config)
        cfg.target_directory = app_config.target_directory

        # feed this sub‐list of stands through the normal run_modes
        current = stands
        for mode in cfg.run_modes:
            runner = mode_runners[mode]
            current = runner(cfg, control_structure, current)
    


    _, dirs, files = next(os.walk(app_config.target_directory))
    if len(dirs) == 0 and len(files) == 0:
        os.rmdir(app_config.target_directory)

    print_logline("Exiting successfully")
    return 0


if __name__ == '__main__':
    code = main()
    sys.exit(code)
