from importlib import import_module
from lukefi.metsi.domain.data_collection.biomass_repola import calculate_biomass
from lukefi.metsi.domain.data_collection.cross_cutting import cross_cut_felled_trees, cross_cut_standing_trees
from lukefi.metsi.domain.data_collection.net_present_value import calculate_npv
from lukefi.metsi.domain.data_collection.marshalling import report_collectives, report_state, collect_properties, \
    collect_standing_tree_properties, collect_felled_tree_properties, report_period
from lukefi.metsi.domain.natural_processes.grow_acta import grow_acta
from lukefi.metsi.domain.forestry_operations.thinning import first_thinning, thinning_from_above, thinning_from_below, report_overall_removal, \
    even_thinning
from lukefi.metsi.domain.forestry_operations.clearcut import clearcutting
from lukefi.metsi.domain.forestry_operations.planting import planting

operation_lookup = {
    'grow_acta': grow_acta,
    'thinning_from_below': thinning_from_below,
    'thinning_from_above': thinning_from_above,
    'first_thinning': first_thinning,
    'even_thinning': even_thinning,
    'planting': planting,
    'clearcutting': clearcutting,
    'calculate_biomass': calculate_biomass,
    'report_biomass': calculate_biomass,
    'report_overall_removal': report_overall_removal,
    'cross_cut_felled_trees': cross_cut_felled_trees,
    'cross_cut_standing_trees': cross_cut_standing_trees,
    'report_collectives': report_collectives,
    'report_state': report_state,
    'collect_properties': collect_properties,
    'collect_standing_tree_properties': collect_standing_tree_properties,
    'collect_felled_tree_properties': collect_felled_tree_properties,
    'report_period': report_period,
    'calculate_npv': calculate_npv
}

def try_register(mod: str, func: str):
    try:
        operation_lookup[func] = getattr(import_module(mod), func)
    except ImportError:
        pass


# only register grow_motti or grow_fhk when pymotti is installed
try_register("forestry.natural_processes.grow_motti", "grow_motti")
try_register("forestry.natural_processes.grow_fhk", "grow_fhk")
try_register("lukefi.metsi.domain.natural_processes.grow_continuous", "grow_continuous")
