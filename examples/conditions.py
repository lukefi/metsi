from lukefi.metsi.domain.forestry_types import ForestCondition
from lukefi.metsi.domain.forestry_types import ForestOpPayload
from lukefi.metsi.domain.pre_ops import generate_reference_trees, preproc_filter, scale_area_weight
from lukefi.metsi.domain.events import GrowActa
from lukefi.metsi.sim.simulation_instruction import SimulationInstruction
from lukefi.metsi.sim.generators import Alternatives, Sequence, Event


def do_a_thing(x):
    """A treatment of some kind."""
    return x


def do_another_thing(x):
    """Another type of treatment."""
    return x


def do_yet_another_thing(x):
    """Yeat another type of treatment."""
    return x


def first_condition_check(t: int, x: ForestOpPayload):
    # Some complex condition check here.
    _, _ = t, x
    return True


def second_condition_check(t: int, x: ForestOpPayload):
    # Some complex condition check here.
    _, _ = t, x
    return True


# Conditions can be created by wrapping a predicate function:
first_condition = ForestCondition(first_condition_check)
second_condition = ForestCondition(second_condition_check)


# Conditions can also be created with the decorator syntax:
@ForestCondition
def third_condition(t: int, x: ForestOpPayload):
    # Some complex condition check here.
    _, _ = t, x
    return True


control_structure = {
    "app_configuration": {
        "state_format": "vmi13",  # options: fdm, vmi12, vmi13, xml, gpkg
        # "state_input_container": "csv",  # Only relevant with fdm state_format. Options: pickle, json
        # "state_output_container": "csv",  # options: pickle, json, csv, null
        # "derived_data_output_container": "pickle",  # options: pickle, json, null
        "formation_strategy": "partial",
        "evaluation_strategy": "depth",
        "run_modes": ["preprocess", "simulate"]
    },
    "preprocessing_operations": [
        scale_area_weight,
        generate_reference_trees,  # reference trees from strata, replaces existing reference trees
        preproc_filter
    ],
    "preprocessing_params": {
        generate_reference_trees: [
            {
                "n_trees": 10,
                "method": "weibull",
                "debug": False
            }
        ],
        preproc_filter: [
            {
                "remove trees": "sapling or stems_per_ha == 0",
                "remove stands": "(site_type_category == None) or (site_type_category == 0)",  # not reference_trees
            }
        ]
    },
    "simulation_instructions": [
        SimulationInstruction(
            time_points=[2025, 2030, 2035],
            events=[
                Sequence([
                    Alternatives([
                        Event(do_a_thing,
                              preconditions=[
                                  # Conditions can be combined with | and & operators.
                                  # Here do_a_thing will be performed if the year is 2025 or any time that the last
                                  # cutting method was 1.
                                  ForestCondition(lambda t, _: t == 2025) |
                                  ForestCondition(lambda _, x: x.computational_unit.method_of_last_cutting == 1)
                              ]),
                        Event(do_another_thing,
                              preconditions=[
                                  # Combined conditions can also be expressed with just one lambda:.
                                  # This time do_another_thing will be performed the year 2030 for all non-auxiliary
                                  # stands.
                                  ForestCondition(
                                      lambda t, x: (t == 2030) and (not x.computational_unit.auxiliary_stand))
                              ]),
                        Event(do_yet_another_thing,
                              # More complex conditions can be formulated in separate modules, such as pre-made
                              # libraries, and combined freely in non-trivial ways.
                              preconditions=[
                                  (first_condition & second_condition) | (third_condition)
                              ])
                    ]),
                    GrowActa()
                ])
            ]
        )
    ]
}

__all__ = ['control_structure']
