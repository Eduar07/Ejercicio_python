from pathlib import Path

from domain.models import EmployeeMetric
from adapters.excel_reader import read_excel, read_master_excel
from domain.business_rules import match_employees, apply_business_rules


def process_metric(weekly_file: Path, master_file: Path) -> list[EmployeeMetric]:

    weekly_employees = read_excel(weekly_file)

    master_employees = read_master_excel(master_file)

    matched_employees = match_employees(
        weekly_employees,
        master_employees
    )

    employees = apply_business_rules(
        matched_employees
    )

    return employees