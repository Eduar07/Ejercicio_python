from pathlib import Path
from application.process_weekly_metrics import process_metric
from adapters.storage import output_exists

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
    save_workbook,
)


def main() -> None:

    weekly_file = Path("data/Input/AT 05.04 - 05.08.xlsx")

    master_file = Path("data/Input/AT_Employees.xlsx")

    output_file = Path("data/Output/result.xlsx")

    week_data = process_metric(weekly_file, master_file)

    if output_exists(output_file):
        
        workbook, worksheet = load_output_workbook(output_file)
        
    else:
        
        workbook, worksheet = create_workbook()

    start_row = get_next_block_start_row(worksheet)

    write_week_range(worksheet, week_data.week_start, week_data.week_end, start_row)

    write_headers(worksheet, start_row)

    apply_column_colors(worksheet, start_row)

    apply_header_font(worksheet, start_row)

    set_column_width(worksheet)

    write_employees(worksheet, week_data.employees, start_row)

    apply_colors(worksheet, week_data.employees, start_row)

    apply_table_borders(worksheet, week_data.employees, start_row)

    save_workbook(workbook, output_file)


if __name__ == "__main__":
    main()
