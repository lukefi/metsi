from itertools import chain
from typing import Any, Optional
from collections.abc import Callable

from lukefi.metsi.app.app_types import ExportableContainer
from lukefi.metsi.data.formats.util import parse_float
from lukefi.metsi.data.layered_model import PossiblyLayered
from lukefi.metsi.data.model import ForestStand, ReferenceTree, TreeStratum
from lukefi.metsi.data.formats.rst_const import MSBInitialDataRecordConst as msb_meta
from lukefi.metsi.domain.forestry_types import StandList


def rst_float(source: str | int | float | None) -> str:
    if source is not None:
        try:
            return f'{round(float(source), 6):.6f}'
        except ValueError:
            return f'{0:.6f}'
    return f'{0:.6f}'


def msb_metadata(stand: PossiblyLayered[ForestStand]) -> tuple[list[str], list[str], list[str]]:
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
        (len(stand.reference_trees) if stand.reference_trees_soa is None else stand.reference_trees_soa.size) *
            msb_meta.tree_record_length
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
        rst_float(len(stand.reference_trees) if stand.reference_trees_soa is None else stand.reference_trees_soa.size),
        rst_float(msb_meta.tree_record_length)
    ]
    return physical_record_metadata, logical_record_metadata, logical_subrecord_metadata


def c_var_metadata(uid: float | None, cvars_len: int) -> list[str]:
    total_length = 2 + cvars_len
    cvars_meta = map(rst_float, [uid, total_length, 2, cvars_len])
    return list(cvars_meta)


def c_var_rst_row(stand: PossiblyLayered[ForestStand], cvar_decl: list[str]) -> str:
    """ Content structure generation for a C-variable row """
    cvars_meta = c_var_metadata(parse_float(stand.identifier) or stand.stand_id, len(cvar_decl))
    cvars_row = " ".join(chain(
        cvars_meta,
        map(rst_float, stand.get_value_list(cvar_decl)
            )))
    return cvars_row


def rst_forest_stand_rows(stand: PossiblyLayered[ForestStand], additional_vars: list[str]) -> list[str]:
    """Generate RST data file rows (with MSB metadata) for a single ForestStand"""
    result = []
    # Additional variables (C-variables) row
    if additional_vars:
        result.append(c_var_rst_row(stand, additional_vars))
    # Forest stand row
    msb_preliminary_records = msb_metadata(stand)
    result.append(" ".join(chain(
        msb_preliminary_records[0],
        msb_preliminary_records[1],
        map(rst_float, stand.as_rst_row()),
        msb_preliminary_records[2]
    )))
    # Reference tree row(s)
    if stand.reference_trees_soa is not None:
        for i in range(stand.reference_trees_soa.size):
            result.append(" ".join(map(rst_float, stand.reference_trees_soa.as_rst_row(i))))
    else:
        for tree in stand.reference_trees:
            result.append(" ".join(map(rst_float, tree.as_rst_row())))
    return result


def rsts_forest_stand_rows(stand: PossiblyLayered[ForestStand]) -> list[str]:
    """Generate RSTS data file rows for a single ForestStand """
    result = []
    result.append(" ".join(chain(
        [str(parse_float(stand.identifier) or stand.stand_id)],
        map(rst_float, stand.as_rst_row())
    )))
    for stratum in stand.tree_strata:
        result.append(" ".join(map(rst_float, stratum.as_rsts_row())))
    return result


def csv_value(source: Any) -> str:
    if source is None:
        return "None"
    return str(source)


def stand_to_csv_rows(stand: PossiblyLayered[ForestStand], delimeter: str,
                      additional_vars: Optional[list[str]]) -> list[str]:
    """converts the :stand:, its reference trees and tree strata to csv rows."""
    result = []
    result.append(delimeter.join(map(csv_value, stand.as_internal_csv_row(additional_vars))))
    result.extend(
        map(
            lambda tree: delimeter.join(
                map(
                    csv_value,
                    tree.as_internal_csv_row())),
            stand.reference_trees)
    )
    result.extend(
        map(
            lambda stratum: delimeter.join(
                map(
                    csv_value,
                    stratum.as_internal_csv_row())),
            stand.tree_strata)
    )
    return result


def stands_to_csv_content(container: ExportableContainer[PossiblyLayered[ForestStand]], delimeter: str) -> list[str]:
    stands = container.export_objects
    additional_vars = container.additional_vars
    result = []
    for stand in stands:
        result.extend(stand_to_csv_rows(stand, delimeter, additional_vars))
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


def outputtable_rows(container: ExportableContainer[PossiblyLayered[ForestStand]], formatter: Callable[[
                     PossiblyLayered[ForestStand], list[str]], list[str]]) -> list[str]:
    stands = container.export_objects
    additional_vars = container.additional_vars or []
    result = []
    for stand in stands:
        result.extend(formatter(stand, additional_vars))
    return result


def stands_to_rst_content(container: ExportableContainer[PossiblyLayered[ForestStand]]) -> list[str]:
    """Generate RST file contents for the given list of ForestStand"""
    return outputtable_rows(container, rst_forest_stand_rows)


def stands_to_rsts_content(container: ExportableContainer[PossiblyLayered[ForestStand]]) -> list[str]:
    """Generate RSTS file contents for the given list of ForestStand"""
    return outputtable_rows(container, lambda stand, additional_vars: rsts_forest_stand_rows(stand))


def mela_par_file_content(cvar_names: list[str]) -> list[str]:
    """ Par file content generalizes over all stands. Only single stand is needed """
    content = [f'#{vname.upper()}' for vname in cvar_names]
    content.insert(0, 'C_VARIABLES')
    return content
