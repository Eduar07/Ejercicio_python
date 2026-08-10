'''
Administrar carpetas y archivos
'''

from domain.errors import ATError
from infrastructure.config import PATHS
from pathlib import Path


def list_input_files() -> list[Path]:
    input_folder = PATHS['input']


    if not input_folder.exists():
        raise ATError(
            "ERR001",
            f"La carpeta {input_folder} no existe"
        )

    input_files  = list(input_folder.glob("*.xlsx"))

    if not input_files:
        raise ATError(
            "ERR002",
            "No existen archivos Excel para procesar"
        )

    return input_files


def get_employees_path() -> Path:
    return PATHS['parametric']/"AT_Employees.xlsx"


def get_log_path(year: int) -> Path:
    return PATHS['logs']/ str(year)/ "AT_Process_Log.xlsx"

def ensure_directories() -> None:
    for folder in PATHS.values():
        folder.mkdir(parents=True, exist_ok=True)
