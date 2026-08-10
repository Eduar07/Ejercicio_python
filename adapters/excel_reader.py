'''
KeyError
Es un error que aparece cuando intentas acceder a una clave que no existe.
try/except
"¿Puede Python o una librería fallar haciendo esta operación?"
if + raise
"La operación funciona, pero ¿el resultado cumple las reglas del negocio/sistema?"
'''
from domain.models import WeekData, EmployeeMetric, MasterEmployee
from pathlib import Path
import openpyxl
from infrastructure.config import SHEET_NAME
from infrastructure.config import SHEET_MASTER,START_ROW_MASTER,HEADER_ROW_MASTER
from infrastructure.config import START_ROW
from infrastructure.config import HEADER_ROW
from domain.models import EmployeeMetric
from domain.errors import ATError
from infrastructure.config import WEEKLY_COLUMNS,MASTER_COLUMNS



def validate_headers(headers: list[str]) -> None:
    if headers != WEEKLY_COLUMNS:
        raise ATError(
            "ERR006",
            "Las columnas del archivo Excel no coinciden con la estructura esperada"
        )


def validate_master_headers(headers_master: list[str]) -> None:
    if headers_master != MASTER_COLUMNS:
        raise ATError(
            "ERR006",
            "Las columnas del archivo Excel no coinciden con la estructura esperada"
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
    for row in worksheetmaster.iter_rows(min_row = HEADER_ROW_MASTER, max_row= HEADER_ROW_MASTER):
        for cell in row:
            headers_master.append(cell.value)
    return headers_master

def create_column_map(headers: list[str]) -> dict[str, int]:
    column_map = { }
    for index, header in enumerate(headers):
        column_map[header] = index

    return column_map

def create_column_map_masater(header_master: list[str] -> dict[str, int]):
    column_map_master = {}
    for index, header in enumerate(header_master):
        column_map_master[header] = index

    return column_map_master



def parse_employees( worksheet,column_map: dict[str, int],source_file: str) -> list[EmployeeMetric]:
    employees = []

    for row in worksheet.iter_rows(min_row=START_ROW):

        employee = EmployeeMetric(
            name=row[column_map["Name"]].value,
            department=row[column_map["Department"]].value,
            productive_active_hours=row[column_map["Productive Active Hrs"]].value,
            productive_passive_hours=row[column_map["Productive Passive Hrs"]].value,
            total_hours=row[column_map["Total Productive Hrs"]].value,
            active_days=row[column_map["Active Days"]].value,
            goal=row[column_map["GOAL"]].value,
            hours_per_day=row[column_map["Productive Hrs/Day"]].value,
            comments=row[column_map["Comments"]].value,
            source_file=source_file
        )

        employees.append(employee)

    return employees


def parse_master_employees(worksheetmaster, column_map:dict[str, int]) -> list[MasterEmployee]:

    master = []

    for row in worksheetmaster.iter_rows(min_row=START_ROW_MASTER):

            master_employee = MasterEmployee(
                employee_id=row[column_map["EmployeeID"]].value,
                name=row[column_map["Name"]].value,
                email=row[column_map["Email"]].value,
                status=row[column_map["Status"]].value
            )
    
            master.append(master_employee)
    
    return master





def read_excel(file_path: Path) -> list[MasterEmployee]:

    try:
        workbook = openpyxl.load_workbook(file_path)

    except Exception:
        raise ATError(
            "ERR004",
            f"No se pudo abrir el archivo {file_path.name}"
        )


    try:
        worksheetmaster = workbook[SHEET_MASTER]

    except KeyError:
        raise ATError(
            "ERR005",
            f"La hoja {SHEET_MASTER} no existe"
        )


    headers = get_headers(worksheetmaster)

    validate_headers(headers)

    column_map = create_column_map(headers)

    employees = parse_employees(
        worksheetmaster,
        column_map,
        file_path.name
    )

    return employees




def read_excel(file_path: Path) -> list[EmployeeMetric]:

    try:
        workbook = openpyxl.load_workbook(file_path)

    except Exception:
        raise ATError(
            "ERR004",
            f"No se pudo abrir el archivo {file_path.name}"
        )


    try:
        worksheet = workbook[SHEET_NAME]

    except KeyError:
        raise ATError(
            "ERR005",
            f"La hoja {SHEET_NAME} no existe"
        )


    headers = get_headers(worksheet)

    validate_headers(headers)

    column_map = create_column_map(headers)

    employees = parse_employees(
        worksheet,
        column_map,
        file_path.name
    )

    return employees
