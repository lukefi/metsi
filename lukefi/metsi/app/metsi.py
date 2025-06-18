import os
import sys
import copy

# TODO: find out what triggers FutureWarning behaviour in numpy
import warnings
import traceback
warnings.simplefilter(action='ignore', category=FutureWarning)

from lukefi.metsi.app.preprocessor import (
    preprocess_stands,
    slice_stands_by_percentage, 
    slice_stands_by_size
    )


from lukefi.metsi.app.app_io import parse_cli_arguments, MetsiConfiguration, generate_application_configuration, RunMode
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.domain.forestry_types import StandList
from lukefi.metsi.app.export import export_files, export_preprocessed
from lukefi.metsi.app.file_io import prepare_target_directory, read_stands_from_file, \
    read_full_simulation_result_dirtree, write_full_simulation_result_dirtree, read_control_module
from lukefi.metsi.app.post_processing import post_process_alternatives
from lukefi.metsi.app.simulator import simulate_alternatives
from lukefi.metsi.app.console_logging import print_logline


def preprocess(config: MetsiConfiguration, control: dict, stands: StandList) -> StandList:
    print_logline("Preprocessing...")
    result = preprocess_stands(stands, control)
    return result


def simulate(config: MetsiConfiguration, control: dict, stands: StandList) -> SimResults:
    print_logline("Simulating alternatives...")
    result = simulate_alternatives(config, control, stands)
    if config.state_output_container is not None or config.derived_data_output_container is not None:
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


def main() -> int:
    cli_arguments = parse_cli_arguments(sys.argv[1:])
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


        if app_config.run_modes[0] in [RunMode.PREPROCESS, RunMode.SIMULATE]:
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
        # cfg.target_directory = slice_target  # 🔁 leave this commented
        cfg.target_directory = app_config.target_directory  # ✅ use original

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
