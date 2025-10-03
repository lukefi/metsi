from functools import cache
from typing import Optional
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.sim.collected_data import CollectedData, OpTuple
from lukefi.metsi.data.model import ForestStand
from lukefi.metsi.data.enums.internal import TreeSpecies
from lukefi.metsi.domain.utils.enums import SiteTypeKey, SoilPreparationKey, RegenerationKey
from lukefi.metsi.domain.utils.conversion import site_type_to_key
from lukefi.metsi.domain.collected_types import PriceableOperationInfo
from lukefi.metsi.app.utils import MetsiException


DEFAULT_INSTRUCTIONS = {
    SiteTypeKey.OMT: {
        'species': 1,
        'stems/ha': 2000,
        'soil preparation': 3
    },
    SiteTypeKey.MT: {
        'species': 1,
        'stems/ha': 2000,
        'soil preparation': 3
    },
    SiteTypeKey.VT: {
        'species': 1,
        'stems/ha': 2000,
        'soil preparation': 1
    },
    SiteTypeKey.CT: {
        'species': 1,
        'stems/ha': 2000,
        'soil preparation': 1
    }
}


@cache
def _create_planting_instructions_table(file_path: str) -> list:
    contents = None
    with open(file_path, "r", encoding="utf-8") as f:
        contents = f.read()
    table = [row.split() for row in contents.split('\n')]

    if len(table) != 4 or len(table[0]) != 3:
        raise MetsiException("Planting instructions file has unexpected structure. Expected 4 rows and 5 columns, "
                             f"got {len(table)} rows and {len(table[0])} columns")
    return table


def _get_planting_instructions_from_parameter_file_contents(file_path: str) -> dict:
    instructions_table = _create_planting_instructions_table(file_path)
    instructions = {
        SiteTypeKey.OMT: {
            'species': int(instructions_table[0][0]),
            'stems/ha': int(instructions_table[0][1]),
            'soil preparation': int(instructions_table[0][2])
        },
        SiteTypeKey.MT: {
            'species': int(instructions_table[1][0]),
            'stems/ha': int(instructions_table[1][1]),
            'soil preparation': int(instructions_table[1][2])
        },
        SiteTypeKey.VT: {
            'species': int(instructions_table[2][0]),
            'stems/ha': int(instructions_table[2][1]),
            'soil preparation': int(instructions_table[2][2])
        },
        SiteTypeKey.CT: {
            'species': int(instructions_table[3][0]),
            'stems/ha': int(instructions_table[3][1]),
            'soil preparation': int(instructions_table[3][2])
        }
    }
    return instructions


def _get_planting_instructions(site_type_category: int, file_path_instructions: Optional[str] = None) -> dict:
    site_type_key = site_type_to_key(site_type_category)
    if file_path_instructions is not None:
        instructions = _get_planting_instructions_from_parameter_file_contents(file_path_instructions)
        regen = instructions[site_type_key]
    else:
        regen = DEFAULT_INSTRUCTIONS[site_type_key]
    return regen


def _plant(stand: PossiblyLayered[ForestStand],
           collected_data: CollectedData,
           tag: str,
           regen_species: TreeSpecies,
           rt_count: int,
           rt_stems: int,
           soil_preparation: SoilPreparationKey
           ) -> OpTuple[ForestStand]:

    regeneration_description = {
        'regeneration': RegenerationKey.PLANTED,
        'soil preparation': soil_preparation,
        'species': regen_species,
        'stems_per_ha': rt_count * rt_stems
    }

    stand.reference_trees.create([
        {
            "identifier": stand.identifier + f"-{i}-tree",
            "stems_per_ha": rt_stems / rt_count,
            "species": regen_species,
            "breast_height_diameter": 0,
            "breast_height_age": 0,
            "biological_age": 1,
            "height": 0.3,
            "sapling": True
        } for i in range(rt_count)
    ])

    collected_data.store(tag, regeneration_description)
    collected_data.extend_list_result(
        "renewal",
        [PriceableOperationInfo(
            operation="planting",
            units=stand.area,  # TODO: planting may not be priced per hectare
            time_point=collected_data.current_time_point)]
    )

    return (stand, collected_data)


def planting(payload: OpTuple[ForestStand], /, **operation_parameters) -> OpTuple[ForestStand]:
    """ Checks weather stand has reference trees, if not function plant is called """
    stand, collected_data = payload
    tree_count = operation_parameters.get('tree_count', 10)

    if len(stand.reference_trees) > 0:
        return payload

    instructions_path = operation_parameters.get('planting_instructions', None)
    if stand.site_type_category is None:
        raise MetsiException(f"No site type category defined for stand {stand.stand_id}")

    regen = _get_planting_instructions(int(stand.site_type_category), instructions_path)
    stand, output_planting = _plant(stand,
                                    collected_data,
                                    "regeneration",
                                    TreeSpecies(regen['species']),
                                    tree_count,
                                    regen['stems/ha'],
                                    regen['soil preparation'])
    return (stand, output_planting)
