from lukefi.metsi.domain.collected_types import PriceableOperationInfo
from lukefi.metsi.sim.core_types import OpTuple
from lukefi.metsi.data.model import ForestStand


def _store_renewal_collection(payload: OpTuple[ForestStand], op_tag: str):
    stand, collected_data = payload
    op_info = PriceableOperationInfo(operation=op_tag, units=stand.area, time_point=collected_data.current_time_point)
    collected_data.extend_list_result("renewal", [op_info])


def clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 400'''
    _ = operation_parameters
    tag = 'clearing'
    _store_renewal_collection(payload, tag)
    return payload


def mechanical_clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 410'''
    _ = operation_parameters
    tag = 'mechanical_clearing'
    _store_renewal_collection(payload, tag)
    return payload


def mechanical_chemical_clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 420'''
    _ = operation_parameters
    tag = 'mechanical_chemical_clearing'
    _store_renewal_collection(payload, tag)
    return payload


def prevention_of_aspen_saplings(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 440'''
    _ = operation_parameters
    tag = 'prevention_of_aspen_saplings'
    _store_renewal_collection(payload, tag)
    return payload


def clearing_before_cutting(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 450'''
    _ = operation_parameters
    tag = 'clearing_before_cutting'
    _store_renewal_collection(payload, tag)
    return payload


def complementary_planting(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 600'''
    _ = operation_parameters
    tag = 'complementary_planting'
    _store_renewal_collection(payload, tag)
    return payload


def complementary_sowing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 630'''
    _ = operation_parameters
    tag = 'complementary_sowing'
    _store_renewal_collection(payload, tag)
    return payload


def mechanical_hay_prevention(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 640'''
    _ = operation_parameters
    tag = 'mechanical_hay_prevention'
    _store_renewal_collection(payload, tag)
    return payload


def chemical_hay_prevention(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 650'''
    _ = operation_parameters
    tag = 'chemical_hay_prevention'
    _store_renewal_collection(payload, tag)
    return payload


def mechanical_clearing_other_species(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 660'''
    _ = operation_parameters
    tag = 'mechanical_clearing_other_species'
    _store_renewal_collection(payload, tag)
    return payload


def chemical_clearing_other_species(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 670'''
    _ = operation_parameters
    tag = 'chemical_clearing_other_species'
    _store_renewal_collection(payload, tag)
    return payload


def mechanical_chemical_clearing_other_species(
        payload: OpTuple[ForestStand],
        **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 680'''
    _ = operation_parameters
    tag = 'mechanical_chemical_clearing_other_species'
    _store_renewal_collection(payload, tag)
    return payload


def hole_clearing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 690'''
    _ = operation_parameters
    tag = 'hole_clearing'
    _store_renewal_collection(payload, tag)
    return payload


def ditching(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 930'''
    _ = operation_parameters
    tag = 'ditching'
    _store_renewal_collection(payload, tag)
    return payload


def reconditioning_ditching(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 940'''
    _ = operation_parameters
    tag = 'reconditioning_ditching'
    _store_renewal_collection(payload, tag)
    return payload


def ditch_blocking(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 950'''
    _ = operation_parameters
    tag = 'ditch_blocking'
    _store_renewal_collection(payload, tag)
    return payload


def root_rot_prevention(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 990'''
    _ = operation_parameters
    tag = 'root_rot_prevention'
    _store_renewal_collection(payload, tag)
    return payload


def other_regeneration(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 999'''
    _ = operation_parameters
    tag = 'other_regeneration'
    _store_renewal_collection(payload, tag)
    return payload


def soil_preparation(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 501'''
    _ = operation_parameters
    tag = 'soil_preparation'
    _store_renewal_collection(payload, tag)
    return payload


def scalping(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 510'''
    _ = operation_parameters
    tag = 'scalping'
    _store_renewal_collection(payload, tag)
    return payload


def mounding_by_scalping(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 520'''
    _ = operation_parameters
    tag = 'mounding_by_scalping'
    _store_renewal_collection(payload, tag)
    return payload


def mounding_by_ground_turning(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 521'''
    _ = operation_parameters
    tag = 'mounding_by_ground_turning'
    _store_renewal_collection(payload, tag)
    return payload


def furrow_mounding(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 522'''
    _ = operation_parameters
    tag = 'furrow_mounding'
    _store_renewal_collection(payload, tag)
    return payload


def harrowing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 530'''
    _ = operation_parameters
    tag = 'harrowing'
    _store_renewal_collection(payload, tag)
    return payload


def ploughing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 540'''
    _ = operation_parameters
    tag = 'ploughing'
    _store_renewal_collection(payload, tag)
    return payload


def mounding_by_ditching(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 550'''
    _ = operation_parameters
    tag = 'mounding_by_ditching'
    _store_renewal_collection(payload, tag)
    return payload


def field_preparation(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 560'''
    _ = operation_parameters
    tag = 'field_preparation'
    _store_renewal_collection(payload, tag)
    return payload


def controlled_burning(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 570'''
    _ = operation_parameters
    tag = 'controlled_burning'
    _store_renewal_collection(payload, tag)
    return payload


def digger_scalping(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 580'''
    _ = operation_parameters
    tag = 'digger_scalping'
    _store_renewal_collection(payload, tag)
    return payload


def soil_preparation_by_tree_stump_lifting(
        payload: OpTuple[ForestStand],
        **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 585'''
    _ = operation_parameters
    tag = 'soil_preparation_by_tree_stump_lifting'
    _store_renewal_collection(payload, tag)
    return payload


def cross_harrowing(payload: OpTuple[ForestStand], **operation_parameters) -> OpTuple[ForestStand]:
    '''SMK operation code 590'''
    _ = operation_parameters
    tag = 'cross_harrowing'
    _store_renewal_collection(payload, tag)
    return payload
