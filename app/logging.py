import time

from forestdatamodel.model import ForestStand

import forestry.operations

start_time = time.time_ns()


def runtime_now() -> float:
    global start_time
    return round((time.time_ns() - start_time) / 1000000000, 1)


def print_logline(message: str):
    print("{} {}".format(runtime_now(), message))


def print_stand_result(stand: ForestStand):
    print("volume {}".format(forestry.operations.compute_volume(stand)))


def print_run_result(results: dict):
    for id in results.keys():
        for i, result in enumerate(results[id]):
            print("{} variant {} result: ".format(id, i), end='')
            print_stand_result(result.simulation_state)
            last_volume_reporting_aggregate = result.aggregated_results.prev('report_volume')
            last_biomass_reporting_aggregate = result.aggregated_results.prev('report_biomass')
            last_removal_reporting_aggregate = result.aggregated_results.prev('report_overall_removal')
            print("variant {} growth report: {}".format(i, last_volume_reporting_aggregate))
            print("variant {} biomass report: {}".format(i, last_biomass_reporting_aggregate))
            print("variant {} thinning report: {}".format(i, last_removal_reporting_aggregate))
