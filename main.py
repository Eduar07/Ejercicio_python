from pathlib import Path
from datetime import datetime

from application.process_weekly_metrics import process_metric

from adapters.storage import (
    output_exists,
    get_output_path,
)

from adapters.logger import write_log_entry

from adapters.excel_write import (
    create_workbook,
    write_week_range,
    write_headers,
    write_employees,
    apply_column_colors,
    apply_header_font,
    set_column_width,
    apply_colors,
    apply_table_borders,
    get_next_block_start_row,
    load_output_workbook,
    week_already_exists,
    save_workbook,
)

from domain.errors import ATError
from domain.model import LogEntry


def main() -> None:

    weekly_file = Path("data/Input/AT 05.11 - 05.15.xlsx")
    master_file = Path("data/Input/AT_Employees.xlsx")

    try:

        week_data = process_metric(
            weekly_file,
            master_file,
        )

        output_file = get_output_path(
            week_data.week_start.year,
            week_data.week_start.month,
        )

        if output_exists(output_file):
            workbook, worksheet = load_output_workbook(output_file)
        else:
            workbook, worksheet = create_workbook()

        if week_already_exists(
            worksheet,
            week_data.week_start,
            week_data.week_end,
        ):
            print("Week already exists. Nothing to process.")
            return

        start_row = get_next_block_start_row(worksheet)

        write_week_range(
            worksheet,
            week_data.week_start,
            week_data.week_end,
            start_row,
        )

        write_headers(
            worksheet,
            start_row,
        )

        apply_column_colors(
            worksheet,
            start_row,
        )

        apply_header_font(
            worksheet,
            start_row,
        )

        set_column_width(worksheet)

        write_employees(
            worksheet,
            week_data.employees,
            start_row,
        )

        apply_colors(
            worksheet,
            week_data.employees,
            start_row,
        )

        apply_table_borders(
            worksheet,
            week_data.employees,
            start_row,
        )

        save_workbook(
            workbook,
            output_file,
        )

    except ATError as error:

        if error.code == "ERR015":
            status = "SUCCESS"
        elif error.code == "ERR013":
            status = "PENDING"
        else:
            status = "ERROR"

        log_entry = LogEntry(
            source_file=weekly_file.name,
            execution_date=datetime.now(),
            status=status,
            error_message=error.detail,
            error_code=error.code,
        )

        write_log_entry(log_entry)

        raise


if __name__ == "__main__":
    main()