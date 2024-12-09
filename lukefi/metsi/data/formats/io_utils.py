from itertools import chain
from typing import Any
from collections.abc import Callable

from lukefi.metsi.data.formats.util import parse_float
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.data.formats.rst_const import MSBInitialDataRecordConst as msb_meta
from lukefi.metsi.domain.forestry_types import StandList


def recreate_stand_indices(stands: StandList) -> StandList:
    for idx, stand in enumerate(stands):
        stand.set_identifiers(idx + 1)
    return stands


def recreate_tree_indices(trees: list[ReferenceTree]) -> list[ReferenceTree]:
    for idx, tree in enumerate(trees):
        tree.tree_number = idx + 1
    return trees


def cleaned_output(stands: StandList) -> StandList:
    """Recreate forest stands for output:
        1) filtering out non-living reference trees
        2) recreating indices for reference trees
        3) filtering out non-forestland stands and empty auxiliary stands
        4) recreating indices for stands"""
    for stand in stands:
        stand.reference_trees = [t for t in stand.reference_trees if t.is_living()]
        stand.reference_trees = recreate_tree_indices(stand.reference_trees)
    stands = [s for s in stands if (
        s.is_forest_land()
        and (not s.is_auxiliary() or s.has_trees() or s.has_strata())
    )]
    stands = recreate_stand_indices(stands)
    return stands


def rst_float(source: str or int or float or None) -> str:
    try:
        return f'{round(float(source), 6):.6f}'
    except:
        return f'{0:.6f}'


def msb_metadata(stand: ForestStand) -> tuple[list[str], list[str], list[str]]:
    """
    Generate a triple with:
        MSB physical record metadata
        Initial data record stand metadata
        Initial data record tree set metadata
    """
    # TODO: this is not a desireable change but introduced as a user helper. First column should be stand id number
    # for which we don't have a strict value, as long as it's internally unique in the RST file. User needs
    # back referencing possibility from RST to actual forest stands in Forest Centre source. This is a hack to provide
    # it. VMI stands should remain unaffected since their identifiers are not parseable as float values.
    outputtable_id = parse_float(stand.identifier) or stand.stand_id

    logical_record_length = sum([
        msb_meta.logical_record_metadata_length,
        msb_meta.stand_record_length,
        msb_meta.logical_subrecord_metadata_length,
        len(stand.reference_trees) * msb_meta.tree_record_length
    ])
    physical_record_metadata = [
        rst_float(outputtable_id),  # UID
        str(sum([
            logical_record_length,
            msb_meta.logical_record_header_length
        ]))  # physical record length
    ]
    logical_record_metadata = [
        rst_float(msb_meta.logical_record_type),  # logical record type
        rst_float(logical_record_length),
        rst_float(msb_meta.stand_record_length)
    ]
    logical_subrecord_metadata = [
        rst_float(len(stand.reference_trees)),
        rst_float(msb_meta.tree_record_length)
    ]
    return physical_record_metadata, logical_record_metadata, logical_subrecord_metadata


def c_var_metadata(stand: ForestStand) -> tuple[list[float], list[float], list[float], list[float]]:
    FIXED_TWO = 2
    outputtable_id = parse_float(stand.identifier) or stand.stand_id # UID
    cvars_len = len(stand.additional_data) 
    total_length = FIXED_TWO + cvars_len
    cvars_meta = map(rst_float, [outputtable_id, total_length, FIXED_TWO, cvars_len])
    return tuple([x] for x in cvars_meta)

def c_var_rst_row(stand: ForestStand, c_var_ctrl: dict) -> str:
    if 'rst' in c_var_ctrl:
        stand.add_additional_data_from_rst(c_var_ctrl['rst'])
    # Additional data (a.k.a MELA C-variable) row
    cvars_meta = c_var_metadata(stand)
    cvars_row = " ".join(chain(
        cvars_meta[0],
        cvars_meta[1],
        cvars_meta[2],
        cvars_meta[3],
        map(rst_float, stand.additional_data_as_rst_row()
    )))    
    return cvars_row

#def rst_forest_stand_rows(stand: ForestStand) -> list[str]:
def rst_forest_stand_rows(stand: ForestStand, control: dict) -> list[str]:
    """Generate RST data file rows (with MSB metadata) for a single ForestStand"""
    result = []
    #Add cvariables from rst
    if 'additional_config' in control:
        if 'c_variables' in control['additional_config']:
            result.append(c_var_rst_row(stand, control['additional_config']['c_variables']))
    # Forest stand row
    msb_preliminary_records = msb_metadata(stand)
    result.append(" ".join(chain(
        msb_preliminary_records[0],
        msb_preliminary_records[1],
        map(rst_float, stand.as_rst_row()),
        msb_preliminary_records[2]
    )))
    # Reference tree row(s)
    for tree in stand.reference_trees:
        result.append(" ".join(map(rst_float, tree.as_rst_row())))
    return result


def rsts_forest_stand_rows(stand: ForestStand) -> list[str]:
    """Generate RSTS data file rows for a single ForestStand"""
    result = []
    result.append(" ".join(chain(
        [ str(parse_float(stand.identifier) or stand.stand_id) ],
        map(rst_float, stand.as_rst_row())
    )))
    for stratum in stand.tree_strata:
        result.append(" ".join(map(rst_float, stratum.as_rsts_row())))
    return result


def csv_value(source: Any) -> str:
    if source is None:
        return "None"
    else:
        return str(source)

def stand_to_csv_rows(stand: ForestStand, delimeter: str) -> list[str]:
    """converts the :stand:, its reference trees and tree strata to csv rows."""
    result = []
    result.append(delimeter.join(map(lambda x: csv_value(x), stand.as_internal_csv_row())))
    result.extend(
        map(
            lambda tree: delimeter.join(
                map(
                    lambda x: csv_value(x),
                    tree.as_internal_csv_row())),
            stand.reference_trees)
    )
    result.extend(
        map(
            lambda stratum: delimeter.join(
                map(
                    lambda x: csv_value(x),
                    stratum.as_internal_csv_row())),
            stand.tree_strata)
    )
    return result


def stands_to_csv_content(stands: StandList, delimeter: str) -> list[str]:
    result = []
    for stand in stands:
        result.extend(stand_to_csv_rows(stand, delimeter))
    return result


def csv_content_to_stands(csv_content: list[list[str]]) -> StandList:
    stands = []
    for row in csv_content:
        if row[0] == "stand":
            stands.append(ForestStand.from_csv_row(row))
        elif row[0] == "tree":
            stands[-1].reference_trees.append(ReferenceTree.from_csv_row(row))
        elif row[0] == "stratum":
            stands[-1].tree_strata.append(TreeStratum.from_csv_row(row))

    # once all stands are recreated, add the stand reference to trees and strata
    for stand in stands:
        for tree in stand.reference_trees:
            tree.stand = stand
        for stratum in stand.tree_strata:
            stratum.stand = stand
    return stands


def outputtable_rows(stands: StandList, formatter: Callable[[StandList], list[str]]) -> list[str]:
    result = []
    for stand in cleaned_output(stands):
        result.extend(formatter(stand))
    return result


def stands_to_rst_content(stands: StandList, control: dict) -> list[str]:
    """Generate RST file contents for the given list of ForestStand"""
    return outputtable_rows(stands, lambda stand: rst_forest_stand_rows(stand, control))


def stands_to_rsts_content(stands: StandList) -> list[str]:
    """Generate RSTS file contents for the given list of ForestStand"""
    return outputtable_rows(stands, lambda stand: rsts_forest_stand_rows(stand))

def stands_to_mela_par_file_content(stands: StandList, c_var_ctrl: dict) -> list[str]:
    content = ['C_VARIABLES']
    reference_stand = next(iter(stands))
    content.extend([ k for k in reference_stand.additional_data.keys() ])
    #Add cvariables from rst
    if 'rst' in c_var_ctrl:
        content.extend([k for k in c_var_ctrl['rst'].keys()])
    single_par_row = "\n#".join(content)
    return [single_par_row]
