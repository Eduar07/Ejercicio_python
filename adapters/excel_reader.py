"""
KeyError
An error raised when you try to access a key that does not exist.
try/except
"Can Python or a library fail while performing this operation?"
if + raise
"The operation works, but does the result comply with the business/system rules?"
"""

from datetime import datetime, date
from domain.model import WeekData, EmployeeMetric, MasterEmployee
from pathlib import Path
import openpyxl
from infrastructure.config import SHEET_NAME
from infrastructure.config import SHEET_MASTER, START_ROW_MASTER, HEADER_ROW_MASTER
from infrastructure.config import START_ROW, WEEK_ROW
from infrastructure.config import HEADER_ROW
from domain.errors import ATError
from infrastructure.config import WEEKLY_COLUMNS, MASTER_COLUMNS


def validate_headers(headers: list[str]) -> None:
    if headers != WEEKLY_COLUMNS:
        raise ATError(
            "ERR006", "Excel file columns do not match the expected structure"
        )


def validate_master_headers(headers_master: list[str]) -> None:
    if headers_master != MASTER_COLUMNS:
        raise ATError(
            "ERR006", "Excel file columns do not match the expected structure"
        )


##datatable##
def get_headers(worksheet) -> list[str]:
    headers = []
    for row in worksheet.iter_rows(min_row=HEADER_ROW, max_row=HEADER_ROW):
        for cell in row:
            headers.append(cell.value)
    return headers


def get_master_headers(worksheetmaster) -> list[str]:
    headers_master = []
    for row in worksheetmaster.iter_rows(
        min_row=HEADER_ROW_MASTER, max_row=HEADER_ROW_MASTER
    ):
        for cell in row:
            headers_master.append(cell.value)
    return headers_master


def create_column_map(headers: list[str]) -> dict[str, int]:
    column_map = {}
    for index, header in enumerate(headers):
        column_map[header] = index

    return column_map


def create_column_map_masater(header_master: list[str]) -> dict[str, int]:
    column_map_master = {}
    for index, header in enumerate(header_master):
        column_map_master[header] = index

    return column_map_master


def parse_employees(
    worksheet, column_map: dict[str, int], source_file: str
) -> list[EmployeeMetric]:

    employees = []

    for row in worksheet.iter_rows(min_row=START_ROW):

        name = row[column_map["Name"]].value

        if name is None:
            continue


        employee = EmployeeMetric(
            name=name,
            department=row[column_map["Department"]].value,
            productive_active_hours=row[column_map["Productive Active Hrs"]].value,
            productive_passive_hours=row[column_map["Productive passive Hrs"]].value,
            total_hours=row[column_map["Total Productive Hrs"]].value,
            active_days=row[column_map["Active Days"]].value,
            goal=row[column_map["GOAL"]].value,
            hours_per_day=row[column_map["Productive Hrs/Day"]].value,
            comments=row[column_map["Comments"]].value,
            source_file=source_file,
        )

        employees.append(employee)

    return employees


def parse_master_employees(
    worksheetmaster, column_map_master: dict[str, int]
) -> list[MasterEmployee]:

    master = []

    for row in worksheetmaster.iter_rows(min_row=START_ROW_MASTER):

        employee_id = row[column_map_master["EmployeeID"]].value

        if employee_id is None:
            continue

        master_employee = MasterEmployee(
            employee_id=employee_id,
            name=row[column_map_master["Name"]].value,
            email=row[column_map_master["Email"]].value,
            status=row[column_map_master["Status"]].value,
        )

        master.append(master_employee)

    return master


def read_excel(file_path: Path) -> list[MasterEmployee]:

    try:
        workbook = openpyxl.load_workbook(file_path)

    except Exception:
        raise ATError("ERR004", f"Could not open the file {file_path.name}")

    try:
        worksheetmaster = workbook[SHEET_MASTER]

    except KeyError:
        raise ATError("ERR005", f"Sheet {SHEET_MASTER} does not exist")

    headers_master = get_master_headers(worksheetmaster)

    validate_master_headers(headers_master)

    column_map_master = create_column_map(headers_master)

    master = parse_master_employees(worksheetmaster, column_map_master)

    return master


def read_weekly_excel(file_path: Path) -> WeekData:

    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)

    except Exception:
        raise ATError("ERR004", f"Could not open the file {file_path.name}")

    try:
        worksheet = workbook[SHEET_NAME]

    except KeyError:
        raise ATError("ERR005", f"Sheet {SHEET_NAME} does not exist")

  
    week_start, week_end = parse_week_range(worksheet)

    headers = get_headers(worksheet)

    validate_headers(headers)

    column_map = create_column_map(headers)

    employees = parse_employees(worksheet, column_map, file_path.name)

    week_data = WeekData(
        week_start=week_start,
        week_end=week_end,
        year=week_start.year,
        employees=employees,
    )

    return week_data


def parse_week_range(worksheet) -> tuple[date, date]:

    for row in worksheet.iter_rows(min_row=WEEK_ROW, max_row=WEEK_ROW):
        for cell in row:
            if cell.value != None and "Week:" in cell.value:
                week_text = cell.value
                week_text = week_text.replace("Week:", "").strip()
                week_start_text, week_end_text = week_text.split("-")
                week_start_text = week_start_text.strip()
                week_end_text = week_end_text.strip()
                week_start = datetime.strptime(week_start_text, "%m/%d/%Y").date()

                week_end = datetime.strptime(week_end_text, "%m/%d/%Y").date()

                return week_start, week_end

        raise ATError("ERR012", "No se encontró el rango de semana en el archivo Excel")

    