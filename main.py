from pathlib import Path
from application.process_weekly_metrics import process_metric


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
    save_workbook
)


def main() -> None:

    weekly_file = Path(
        "data/Input/AT 05.04 - 05.08.xlsx"
    )

    master_file = Path(
        "data/Input/AT_Employees.xlsx"
    )

    output_file = Path(
        "data/Output/result.xlsx"
    )

    week_data = process_metric(
        weekly_file,
        master_file
    )

    workbook, worksheet = create_workbook()

    write_week_range(
        worksheet,
        week_data.week_start,
        week_data.week_end
    )

    write_headers(worksheet)

    apply_column_colors(worksheet)

    apply_header_font(worksheet)

    set_column_width(worksheet)

    apply_table_borders(worksheet, week_data.employees)
    
    write_employees(
        worksheet,
        week_data.employees
    )

    apply_colors(
        worksheet,
        week_data.employees
    )

    save_workbook(
        workbook,
        output_file
    )


if __name__ == "__main__":
    main()