from pathlib import Path
from app.app_types import SimResults
from app.file_io import row_writer


def collect_rows_for_events(derived_data: dict, data_source: str) -> list[str]:
    retval = []
    timber_events = derived_data.get('report_state')
    tree_data = derived_data.get('collect_standing_tree_properties')
    for year, report in timber_events.items():
        event_details = collect_timber_data_for_year(report, year)

        for event in event_details:
            header = " ".join([str(event['event_type']), str(event['year']), str(event['source']), str(round(event['total'], 2)), "m3/ha"])
            if data_source == "timber":
                timber_row = " " + " ".join(map(lambda x: str(round(x, 2)), event['values']))
                retval.append(header)
                retval.append(timber_row)
            elif data_source == "trees":
                if event['event_type'] == 'Event':
                    retval.append(header)
                    # TODO: Missing reference to tree data in cross cutting results
                    retval.append("N/A")
                else:
                    tree_rows = map(lambda row: " ".join(map(lambda item: str(round(item, 2)), row)), tree_data.get(year, [[]]))
                    retval.append(header)
                    retval.extend(tree_rows)
    return retval


def collect_timber_data_for_year(report: dict, year: int) -> list[dict]:
    retval = []
    stock = list(report.values())[0:8]
    stocksum = sum(stock)
    timber = list(report.values())[9:18]
    timbersum = sum(timber)
    # TODO: At this moment we have no explicit flag to disambiguate the "State Year" from "Node before Event"
    stock_year_type = 'Node' if timbersum > 0 else 'State'
    if stocksum > 0:
        retval.append(
            {'year': year, 'event_type': stock_year_type, 'total': stocksum, 'values': stock, 'source': 'Stock'})
    if timbersum > 0:
        # TODO: at this moment we can't get the operation type from results
        retval.append({'year': year, 'event_type': 'Event', 'total': timbersum, 'values': timber, 'source': 'thinning'})
    return retval


def prepare_schedule_content(data: SimResults, data_source: str) -> list[str]:
    output_rows = []
    for stand_id, payload in data.items():
        output_rows.append(f"Stand {stand_id} Area {payload[0].simulation_state.area}")
        output_rows.append("")
        for schedule_number, schedule_derived_data in enumerate(map(lambda x: x.aggregated_results, payload)):
            output_rows.append(f"Schedule {schedule_number}")
            prepared = collect_rows_for_events(schedule_derived_data, data_source)
            output_rows.extend(prepared)
    return output_rows


def rm_schedules_events_timber(filepath: Path, data: SimResults):
    """Produce output file collecting state and event year timber volumes for all schedules and stands"""
    content = prepare_schedule_content(data, "timber")
    row_writer(filepath, content)


def rm_schedules_events_trees(filepath: Path, data: SimResults):
    """Produce output file collecting state and event year timber volumes for all schedules and stands"""
    content = prepare_schedule_content(data, "trees")
    row_writer(filepath, content)
