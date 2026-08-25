from pathlib import Path
from datetime import date

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.utils import get_column_letter

from domain.errors import ATError
from domain.model import EmployeeMetric
from infrastructure.config import (
    OUTPUT_SHEET_NAME,
    OUTPUT_COLUMNS,
    COLUMN_WIDTHS,
    YELLOW_FILL_COLOR,
    BLUE_FILL_COLOR,
    YELLOW_COLUMNS,
    COLORS,
    PASSIVE_COLUMN,
    HOURS_DAY_COLUMN,
    PRODUCTIVE_ACTIVE_COLUMN,
    TOTAL_PRODUCTIVE_COLUMN,
    WEEK_ROW_OUTPUT,
)


def create_workbook():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = OUTPUT_SHEET_NAME

    return workbook, worksheet


def load_output_workbook(file_path: Path):
    workbook = openpyxl.load_workbook(file_path)
    worksheet = workbook[OUTPUT_SHEET_NAME]

    return workbook, worksheet


def write_week_range(
    worksheet,
    week_start: date,
    week_end: date,
    start_row: int,
) -> None:

    week_text = (
        f"Week: "
        f"{week_start.strftime('%m/%d/%Y')} - "
        f"{week_end.strftime('%m/%d/%Y')}"
    )

    week_cell = worksheet.cell(
        row=start_row,
        column=1,
        value=week_text,
    )

    week_cell.font = Font(
        bold=True,
        color="FFFFFF",
        size=16,
    )

    week_cell.fill = PatternFill(
        fill_type="solid",
        fgColor="000000",
    )

    week_cell.alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    last_column_letter = get_column_letter(
        len(OUTPUT_COLUMNS)
    )

    worksheet.merge_cells(
        f"A{start_row}:{last_column_letter}{start_row}"
    )


def write_headers(
    worksheet,
    start_row: int,
) -> None:

    for column, header in enumerate(
        OUTPUT_COLUMNS,
        start=1,
    ):
        worksheet.cell(
            row=start_row + 1,
            column=column,
            value=header,
        )


def write_employees(
    worksheet,
    employees: list[EmployeeMetric],
    start_row: int,
) -> None:

    for row_number, employee in enumerate(
        employees,
        start=start_row + 2,
    ):

        values = [
            employee.name,
            employee.department,
            employee.productive_active_hours,
            employee.productive_passive_hours,
            employee.total_hours,
            employee.active_days,
            employee.goal,
            employee.hours_per_day,
            employee.comments,
        ]

        for column, value in enumerate(
            values,
            start=1,
        ):
            cell = worksheet.cell(
                row=row_number,
                column=column,
                value=value,
            )

            if column in (
                HOURS_DAY_COLUMN,
                PRODUCTIVE_ACTIVE_COLUMN,
                PASSIVE_COLUMN,
                TOTAL_PRODUCTIVE_COLUMN,
            ):
                cell.number_format = "0.0"


def apply_colors(
    worksheet,
    employees: list[EmployeeMetric],
    start_row: int,
) -> None:

    green_fill = PatternFill(
        fill_type="solid",
        fgColor=COLORS["green"],
    )

    red_fill = PatternFill(
        fill_type="solid",
        fgColor=COLORS["red"],
    )

    yellow_fill = PatternFill(
        fill_type="solid",
        fgColor=COLORS["yellow"],
    )

    for row_number, employee in enumerate(
        employees,
        start=start_row + 2,
    ):

        color_mapping = {
            HOURS_DAY_COLUMN: employee.color_hours_day,
            PASSIVE_COLUMN: employee.color_passive,
            PRODUCTIVE_ACTIVE_COLUMN: employee.color_active_hrs,
            TOTAL_PRODUCTIVE_COLUMN: employee.color_total_hours,
        }

        for column, color in color_mapping.items():
            if color == "green":
                worksheet.cell(
                    row=row_number,
                    column=column,
                ).fill = green_fill
            elif color == "yellow":
                worksheet.cell(
                    row=row_number,
                    column=column,
                ).fill = yellow_fill
            elif color == "red":
                worksheet.cell(
                    row=row_number,
                    column=column,
                ).fill = red_fill


def save_workbook(
    workbook,
    file_path: Path,
) -> None:

    try:
        workbook.save(file_path)
    except Exception:
        raise ATError(
            "ERR014",
            f"Could not save the file {file_path.name}",
        )


def set_column_width(worksheet) -> None:
    for column, width in COLUMN_WIDTHS.items():
        letter = get_column_letter(column)
        worksheet.column_dimensions[letter].width = width


def apply_column_colors(
    worksheet,
    start_row: int,
) -> None:

    yellow_fill = PatternFill(
        fill_type="solid",
        fgColor=YELLOW_FILL_COLOR,
    )

    blue_fill = PatternFill(
        fill_type="solid",
        fgColor=BLUE_FILL_COLOR,
    )

    for column in range(
        1,
        len(OUTPUT_COLUMNS) + 1,
    ):
        fill = (
            yellow_fill
            if column in YELLOW_COLUMNS
            else blue_fill
        )

        worksheet.cell(
            row=start_row + 1,
            column=column,
        ).fill = fill


def apply_header_font(
    worksheet,
    start_row: int,
) -> None:

    header_font = Font(
        bold=True,
        color="FFFFFF",
    )

    header_alignment = Alignment(
        horizontal="center",
        vertical="center",
    )

    worksheet.row_dimensions[
        start_row + 1
    ].height = 25

    for column in range(
        1,
        len(OUTPUT_COLUMNS) + 1,
    ):
        cell = worksheet.cell(
            row=start_row + 1,
            column=column,
        )

        cell.font = header_font
        cell.alignment = header_alignment


def apply_table_borders(
    worksheet,
    employees: list[EmployeeMetric],
    start_row: int,
) -> None:

    thin_border = Border(
        left=Side(style="thin", color="000000"),
        right=Side(style="thin", color="000000"),
        top=Side(style="thin", color="000000"),
        bottom=Side(style="thin", color="000000"),
    )

    last_row = start_row + len(employees) + 1

    for row in range(
        start_row,
        last_row + 1,
    ):
        for column in range(
            1,
            len(OUTPUT_COLUMNS) + 1,
        ):
            worksheet.cell(
                row=row,
                column=column,
            ).border = thin_border


def get_next_block_start_row(worksheet) -> int:
    if worksheet.max_row <= 1:
        return WEEK_ROW_OUTPUT

    return worksheet.max_row + 4


def week_already_exists(
    worksheet,
    week_start: date,
    week_end: date,
) -> bool:

    expected_text = (
        f"Week: "
        f"{week_start.strftime('%m/%d/%Y')} - "
        f"{week_end.strftime('%m/%d/%Y')}"
    )

    for row in worksheet.iter_rows():
        for cell in row:
            if cell.value == expected_text:
                return True

    return False


def create_empty_week_block(
    worksheet,
    week_start: date,
    week_end: date,
    placeholder_employees: list[EmployeeMetric],
) -> bool:

    if week_already_exists(
        worksheet,
        week_start,
        week_end,
    ):
        return

    start_row = get_next_block_start_row(worksheet)

    write_week_range(
        worksheet,
        week_start,
        week_end,
        start_row,
    )

    write_headers(worksheet, start_row)
    apply_column_colors(worksheet, start_row)
    apply_header_font(worksheet, start_row)
    set_column_width(worksheet)

    write_employees(
        worksheet,
        placeholder_employees,
        start_row,
    )

    apply_table_borders(
        worksheet,
        placeholder_employees,
        start_row,
    )

    return True