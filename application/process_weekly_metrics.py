from pathlib import Path

from domain.models import EmployeeMetric
from adapters.excel_reader import read_weekly_excel, read_master_excel
from domain.business_rules import match_employees, apply_business_rules,detect_cross_month

def process_metric( weekly_file: Path, master_file: Path) -> list[EmployeeMetric]:

    weekly_data = read_weekly_excel(weekly_file)

    cross_month = detect_cross_month(
        weekly_data.week_start,
        weekly_data.week_end
    )

    if cross_month:
        raise ATError(
            "ERR013",
            "The weekly file crosses two months"
        )

    master_employees = read_master_excel(master_file)

    matched_employees = match_employees(
        weekly_data.employees,
        master_employees
    )

    employees = apply_business_rules(
        matched_employees
    )

    return employees