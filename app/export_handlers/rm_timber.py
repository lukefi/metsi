from pathlib import Path
from app.app_types import SimResults
from app.file_io import row_writer


def format_timber_volume_in_event_rows(event: dict) -> list[str]:
    description_row = " ".join([str(event['event_type']), str(event['year']), str(event['source']), str(round(event['total'], 2)), "m3/ha"])
    value_row = " " + " ".join(map(lambda x: str(round(x, 2)), event['values']))
    return [description_row, value_row]


def collect_events_in_schedule(report_state_data) -> list[dict]:
    retval = []
    for year, report in report_state_data.items():
        stock = list(report.values())[0:8]
        stocksum = sum(stock)
        timber = list(report.values())[9:18]
        timbersum = sum(timber)
        # TODO: At this moment we have no explicit flag to disambiguate the "State Year" from "Node before Event"
        stock_year_type = 'Node' if timbersum > 0 else 'State'
        if stocksum > 0:
            retval.append({'year': year, 'event_type': stock_year_type, 'total': stocksum, 'values': stock, 'source': 'Stock'})
        if timbersum > 0:
            # TODO: at this moment we can't get the operation type from results
            retval.append({'year': year, 'event_type': 'Event', 'total': timbersum, 'values': timber, 'source': 'thinning'})
    return retval


def prepare_cross_cut_volumes_content(data: SimResults) -> list[str]:
    output_rows = []
    for stand_id, payload in data.items():
        output_rows.append(f"Stand {stand_id} Area {payload[0].simulation_state.area}")
        output_rows.append("")
        for schedule_number, schedule_derived_data in enumerate(map(lambda x: x.aggregated_results, payload)):
            output_rows.append(f"Schedule {schedule_number}")
            for prepared in collect_events_in_schedule(schedule_derived_data.get('report_state')):
                output_rows.extend(format_timber_volume_in_event_rows(prepared))
            output_rows.append("")

    return output_rows


def rm_schedules_events_timber(filepath: Path, data: SimResults):
    """Produce output file collecting state and event year timber volumes for all schedules and stands"""
    content = prepare_cross_cut_volumes_content(data)
    row_writer(filepath, content)
