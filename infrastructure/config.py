'''
guarda los numeros y nombres que pueden cambiar
from pathlib import Path
Path es la clase.
Path("data") es una instancia de esa clase (el objeto creado).
ruta es la variable que guarda esa instancia.
"data" no es "el objeto", es un argumento (string) que pasas al constructor.
'''

from pathlib import Path
'''config, argumentos de entrada'''
PROJECT_ROOT = Path(__file__).parent.parent

PATHS = {
    "input" : PROJECT_ROOT / "data" / "Input",
    "output" : PROJECT_ROOT / "data" / "Output",
    "logs" : PROJECT_ROOT / "data" / "Logs",
    "parametric" : PROJECT_ROOT / "data" / "Parametric_Files"
}

SHEET_NAME = "Prod + Pass Hours All Dept"
SHEET_MASTER = "HOJA 1"


DATE_FORMAT = "%m/%d/%Y"

WEEKLY_COLUMNS = [
    "Name",
    "Department",
    "Productive Active Hrs",
    "Productive Passive Hrs",
    "Total Productive Hrs",
    "Active Days",
    "GOAL",
    "Productive Hrs/Day",
    "Comments"
]

MASTER_COLUMNS = [
    "EmployeeID",
    "Name",
    "Email",
    "Status"
]


COLORS = {
    "green": "63BE7B",
    "red": "F8696B",
}

STATUSES = {
    "success": "SUCCESS",
    "error": "ERROR",
    "warning": "WARNING",
    "pending": "PENDING"
}

HEADER_ROW = 3
START_ROW = 4
HEADER_ROW_MASTER = 1
START_ROW_MASTER = 2
