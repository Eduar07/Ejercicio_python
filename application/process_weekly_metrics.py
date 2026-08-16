from pathlib import Path
from domain.model import WeekData
from domain.errors import ATError

from adapters.excel_reader import (
    read_weekly_excel,
    read_excel
)

from adapters.excel_write import (
    create_workbook,
    load_output_workbook,
    create_empty_week_block,
    save_workbook,
)

from adapters.storage import (
    get_output_path,
    get_next_month_output_path,
    output_exists,
)

from domain.business_rules import (
    match_employees,
    apply_business_rules,
    detect_cross_month,
    split_cross_month_range,
    build_placeholder_employees,
)
def handle_cross_month(weekly_data: WeekData, master_file: Path) -> bool:
    master_employees = read_excel(master_file)
    placeholders = build_placeholder_employees(master_employees)

    closing_start, closing_end, opening_start, opening_end = split_cross_month_range(
        weekly_data.week_start, weekly_data.week_end
    )

    closing_path = get_output_path(closing_start.year, closing_start.month)
    opening_path = get_next_month_output_path(
        weekly_data.week_start.year, weekly_data.week_start.month
    )

    blocks = [
        (closing_path, closing_start, closing_end),
        (opening_path, opening_start, opening_end),
    ]

    any_created = False

    for file_path, block_start, block_end in blocks:
        if output_exists(file_path):
            workbook, worksheet = load_output_workbook(file_path)
        else:
            workbook, worksheet = create_workbook()

        created = create_empty_week_block(worksheet, block_start, block_end, placeholders)
        if created:
            any_created = True

        save_workbook(workbook, file_path)

    return any_created

def process_metric(weekly_file: Path, master_file: Path) -> WeekData:

    weekly_data = read_weekly_excel(weekly_file)

    cross_month = detect_cross_month(
        weekly_data.week_start,
        weekly_data.week_end
    )

    if cross_month:
        templates_created = handle_cross_month(weekly_data, master_file)

        if templates_created:
            raise ATError(
                "ERR013",
                "The weekly file crosses two months — templates created for manual completion"
            )
        else:
            raise ATError(
                "ERR015",
                "The weekly file crosses two months — templates already existed, nothing changed"
            )

    master_employees = read_excel(master_file)

    matched_employees = match_employees(
        weekly_data.employees,
        master_employees
    )

    weekly_data.employees = apply_business_rules(
        matched_employees
    )

    return weekly_data