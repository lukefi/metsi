from functools import cache
from sim.core_types import AggregatedResults, OpTuple
from forestdatamodel.model import ForestStand, ReferenceTree
from forestdatamodel.enums.internal import TreeSpecies
from forestry.utils.enums import SiteTypeKey, SoilPreparationKey, RegenerationKey
from forestry.utils.conversion import site_type_to_key
from forestry.renewal import PriceableOperationInfo

DEFAULT_INSTRUCTIONS = {
        SiteTypeKey.OMT: {
            'species':2,
            'stems/ha':2200,
            'soil preparation':3
        },
        SiteTypeKey.MT: {
            'species':2,
            'stems/ha':2200,
            'soil preparation':3
        },
        SiteTypeKey.VT: {
            'species':1,
            'stems/ha':2000,
            'soil preparation':1
        },
        SiteTypeKey.CT: {
            'species':1,
            'stems/ha':2000,
            'soil preparation':1
        }
    }

@cache
def create_planting_instructions_table(file_path: str) -> list:
    contents = None
    with open(file_path, "r") as f:
        contents = f.read()
    table = contents.split('\n')
    table = [row.split() for row in table]
    
    if len(table) != 4 or len(table[0]) != 3:
        raise Exception('planting instructions file has unexpected structure. Expected 4 rows and 5 columns, got {} rows and {} columns'.format(len(table), len(table[0])))
    else:
        return table

def get_planting_instructions_from_parameter_file_contents(
    file_path: str,
    ) -> dict:
    instructions = create_planting_instructions_table(file_path)
    INSTRUCTIONS = {
        SiteTypeKey.OMT: {
            'species':int(instructions[0][0]),
            'stems/ha':int(instructions[0][1]),
            'soil preparation':int(instructions[0][2])
        },
        SiteTypeKey.MT: {
            'species':int(instructions[1][0]),
            'stems/ha':int(instructions[1][1]),
            'soil preparation':int(instructions[1][2])
        },
        SiteTypeKey.VT: {
            'species':int(instructions[2][0]),
            'stems/ha':int(instructions[2][1]),
            'soil preparation':int(instructions[2][2])
        },
        SiteTypeKey.CT: {
            'species':int(instructions[3][0]),
            'stems/ha':int(instructions[3][1]),
            'soil preparation':int(instructions[3][2])
        }
    }
    return INSTRUCTIONS

def get_planting_instructions(site_type_category: int, file_path_instructions: str = None) -> dict:
    site_type_key = site_type_to_key(site_type_category)
    if file_path_instructions is not None:
        instructions = get_planting_instructions_from_parameter_file_contents(file_path_instructions)
        regen = instructions[site_type_key]
    else:
         regen = DEFAULT_INSTRUCTIONS[site_type_key]
    return regen

def plant(
    stand: ForestStand, 
    aggr: AggregatedResults, 
    tag: str,
    regen_species: TreeSpecies, 
    rt_count: int,
    rt_stems: int, 
    soil_preparation: SoilPreparationKey
    ) -> OpTuple[ForestStand]:

    for i in range(rt_count):
        tree_id = stand.identifier + f"-{i}-tree"
        tree = ReferenceTree(identifier=tree_id,
                             stems_per_ha=rt_stems/rt_count,
                             species=regen_species,
                             breast_height_diameter=0,
                             breast_height_age=0,
                             biological_age=1,
                             height=0.3,
                             sapling=True)
        stand.reference_trees.append(tree)
    
    regeneration_description = {
        'regeneration': RegenerationKey.PLANTED,
        'soil preparation': soil_preparation,
        'species':regen_species,
        'stems_per_ha': rt_count*rt_stems
    }
    aggr.store(
        tag, regeneration_description
    )
    
    aggr.extend_list_result(
        "renewal", 
        [
            PriceableOperationInfo(
                operation="planting",
                units=stand.area, #TODO: planting may not be priced per hectare 
                time_point=aggr.current_time_point,
                )
        ]
    ) 

    return (stand, aggr)


def planting(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    """checks weather stand has reference trees, if not 
    function plant is called
    """
    stand, simulation_aggregates = payload

    if len(stand.reference_trees)> 0: 
        return payload 
    
    instructions_path = operation_parameters.get('renewal_instructions', None)
    regen = get_planting_instructions(stand.site_type_category, instructions_path)
    stand, output_planting = plant(
                                    stand,
                                    simulation_aggregates,
                                    "regeneration",
                                    TreeSpecies(regen['species']),
                                    10,
                                    regen['stems/ha'],
                                    regen['soil preparation']
                                    )
    return (stand,output_planting)