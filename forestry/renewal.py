from sim.core_types import OpTuple
from forestdatamodel.model import ForestStand


def _store_operation_total_cost(payload: OpTuple[ForestStand], op_tag: str, **operation_parameters):
     stand, aggrs = payload
     cost_per_ha = operation_parameters["cost_per_ha"]
     total_cost = cost_per_ha * stand.area 
     aggregate = {aggrs.current_time_point: total_cost}
     aggrs.upsert_nested(aggregate, "renewal", op_tag)


def clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 400''' 
 tag = 'clearing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mechanical_clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 410''' 
 tag = 'mechanical_clearing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mechanical_chemical_clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 420''' 
 tag = 'mechanical_chemical_clearing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def prevention_of_aspen_saplings(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 440''' 
 tag = 'prevention_of_aspen_saplings' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def clearing_before_cutting(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 450''' 
 tag = 'clearing_before_cutting' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def complementary_planting(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 600''' 
 tag = 'complementary_planting' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def complementary_sowing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 630''' 
 tag = 'complementary_sowing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mechanical_hay_prevention(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 640''' 
 tag = 'mechanical_hay_prevention' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def chemical_hay_prevention(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 650''' 
 tag = 'chemical_hay_prevention' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mechanical_clearing_other_species(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 660''' 
 tag = 'mechanical_clearing_other_species' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def chemical_clearing_other_species(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 670''' 
 tag = 'chemical_clearing_other_species' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mechanical_chemical_clearing_other_species(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 680''' 
 tag = 'mechanical_chemical_clearing_other_species' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def hole_clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 690''' 
 tag = 'hole_clearing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def ditching(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 930''' 
 tag = 'ditching' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def reconditioning_ditching(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 940''' 
 tag = 'reconditioning_ditching' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def ditch_blocking(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 950''' 
 tag = 'ditch_blocking' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def root_rot_prevention(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 990''' 
 tag = 'root_rot_prevention' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def other_regeneration(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 999''' 
 tag = 'other_regeneration' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def soil_preparation(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 501''' 
 tag = 'soil_preparation' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def scalping(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 510''' 
 tag = 'scalping' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mounding_by_scalping(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 520''' 
 tag = 'mounding_by_scalping' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mounding_by_ground_turning(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 521''' 
 tag = 'mounding_by_ground_turning' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def furrow_mounding(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 522''' 
 tag = 'furrow_mounding' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def harrowing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 530''' 
 tag = 'harrowing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def ploughing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 540''' 
 tag = 'ploughing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def mounding_by_ditching(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 550''' 
 tag = 'mounding_by_ditching' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def field_preparation(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 560''' 
 tag = 'field_preparation' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def controlled_burning(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 570''' 
 tag = 'controlled_burning' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def digger_scalping(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 580''' 
 tag = 'digger_scalping' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def soil_preparation_by_tree_stump_lifting(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 585''' 
 tag = 'soil_preparation_by_tree_stump_lifting' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


def cross_harrowing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]: 
 '''SMK operation code 590''' 
 tag = 'cross_harrowing' 
 _store_operation_total_cost(payload, tag, **operation_parameters) 
 return payload 


