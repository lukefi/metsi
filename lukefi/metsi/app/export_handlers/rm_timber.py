from pathlib import Path
from collections import defaultdict
from lukefi.metsi.app.app_types import SimResults
from lukefi.metsi.app.file_io import row_writer
from lukefi.metsi.domain.collected_types import CrossCutResult
from lukefi.metsi.sim.core_types import CollectedData


def scan_operation_type_for_event(year: int, cross_cut: dict[tuple[int, str], list[CrossCutResult]]) -> str:
    val = next(filter(lambda r: r.time_point == year and r.source == "harvested", *cross_cut.values())).operation
    return val


def group_crosscut_by_year_and_source(results: list[CrossCutResult]) -> dict[tuple[int, str], list[CrossCutResult]]:
    grouped = defaultdict(list)
    for r in results:
        grouped[(r.time_point, r.source)].append(r)
    return grouped


def collect_rows_for_events(derived_data: CollectedData, data_source: str) -> list[str]:
    """Create rows for events in a single schedule"""
    retval = []
    timber_events = derived_data.get('report_state')
    standing_tree_data = derived_data.get('collect_standing_tree_properties')
    felled_tree_data = derived_data.get('collect_felled_tree_properties')
    cross_cut_results: list[CrossCutResult] = derived_data.get('cross_cutting')
    grouped = group_crosscut_by_year_and_source(cross_cut_results)

    for year, _ in timber_events.items():
        event_details = collect_timber_data_for_year(year, grouped)

        for event in event_details:
            header = " ".join([str(event['event_type']), str(event['year']), str(
                event['source']), str(round(event['total'], 2)), "m3/ha"])
            if data_source == "timber":
                timber_row = " " + " ".join(map(lambda x: str(round(float(x), 2)), event['values']))
                retval.append(header)
                retval.append(timber_row)
            elif data_source == "trees":
                if event['event_type'] == 'Event':
                    retval.append(header)
                    tree_rows = map(lambda row: " ".join(map(lambda item: str(round(item, 2)), row)),
                                    felled_tree_data.get(year, [[]]))
                    retval.extend(tree_rows)
                else:
                    tree_rows = map(lambda row: " ".join(map(lambda item: str(round(item, 2)), row)),
                                    standing_tree_data.get(year, [[]]))
                    retval.append(header)
                    retval.extend(tree_rows)
    return retval


def find_volumes_for_source(grouped: dict[tuple[int, str], list[CrossCutResult]],
                            year: int, source: str) -> list[float]:
    filtered = grouped.get((year, source), [])

    def volume_sum(species_cond, grade):
        return sum(
            r.volume_per_ha
            for r in filtered
            if species_cond(r.species) and r.timber_grade == grade
        )

    return [
        volume_sum(lambda s: s == 1, 1),
        volume_sum(lambda s: s == 1, 2),
        volume_sum(lambda s: s == 1, 3),
        volume_sum(lambda s: s == 2, 1),
        volume_sum(lambda s: s == 2, 2),
        volume_sum(lambda s: s == 2, 3),
        volume_sum(lambda s: s not in {1, 2}, 1),
        volume_sum(lambda s: s not in {1, 2}, 2),
        volume_sum(lambda s: s not in {1, 2}, 3),
    ]


def collect_timber_data_for_year(
        year: int, cross_cut_results: dict[tuple[int, str], list[CrossCutResult]]) -> list[dict]:
    """Compose collection objects for timber volume details"""
    stock = find_volumes_for_source(cross_cut_results, year, "standing")
    timber = find_volumes_for_source(cross_cut_results, year, "harvested")
    retval = []
    total_stock = sum(stock)
    total_timber = sum(timber)
    # TODO: At this moment we have no explicit flag to disambiguate the "State Year" from "Node before Event"
    stock_year_type = 'Node' if total_timber > 0 else 'State'
    retval.append({'year': year, 'event_type': stock_year_type,
                  'total': total_stock, 'values': stock, 'source': 'Stock'})
    if total_timber > 0:
        #operation = scan_operation_type_for_event(year, cross_cut_results)
        harvested = cross_cut_results.get((year, "harvested"), [])
        operation = scan_operation_type_for_event(year, harvested)
        retval.append({'year': year, 'event_type': 'Event', 'total': total_timber,
                      'values': timber, 'source': operation})
    return retval


def prepare_schedules_file_content(data: SimResults, data_source: str) -> list[str]:
    """
    Create the content rows for Reijo Mykkänen output files for all stands divided into schedules and state/node/event
    years within.

    :param data: SimResults package
    :param data_source: "trees" for standing/harvested tree variables content,
                        "timber" for standing/harvested timber volume content
    :return: list of strings representing file rows
    """
    output_rows = []
    for stand_id, payload in data.items():
        schedule_rows = [f"Stand {stand_id} Area {payload[0].computational_unit.area}"]
        for schedule_number, schedule_derived_data in enumerate(map(lambda x: x.collected_data, payload)):
            rows = [f"Schedule {schedule_number}"]
            rows.extend(collect_rows_for_events(schedule_derived_data, data_source))
            rows.append("")
            schedule_rows.extend(rows)
        schedule_rows.append("")
        output_rows.extend(schedule_rows)
    return output_rows


def rm_schedules_events_timber(filepath: Path, data: SimResults):
    """Produce output file collecting state and event year timber volumes for all schedules and stands"""
    content = prepare_schedules_file_content(data, "timber")
    row_writer(filepath, content)


def rm_schedules_events_trees(filepath: Path, data: SimResults):
    """Produce output file collecting state and event year tree parameters for all schedules and stands"""
    content = prepare_schedules_file_content(data, "trees")
    row_writer(filepath, content)
