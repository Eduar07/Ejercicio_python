'''
Manage folders and files
'''

import shutil
import openpyxl
from adapters.excel_write import create_workbook
from domain.errors import ATError
from infrastructure.config import PATHS,OUTPUT_SHEET_NAME
from pathlib import Path


def list_input_files() -> list[Path]:
    input_folder = PATHS['input']


    if not input_folder.exists():
        raise ATError(
            "ERR001",
            f"Folder {input_folder} does not exist"
        )

    input_files  = list(input_folder.glob("*.xlsx"))

    if not input_files:
        raise ATError(
            "ERR002",
            "No Excel files to process"
        )
    return input_files


def get_employees_path() -> Path:
    return PATHS['parametric']/"AT_Employees.xlsx"


def get_output_path(year: int, month: int) -> Path:
    output_folder = PATHS["ouput"] /str(year)/ f"{month:02d}"
    output_folder.mkdir(parents=True, exist_ok=True)
    return output_folder / f"AT_Metrics_{year}-{month:02d}.xlsx"

def get_log_path(year: int) -> Path:
    return PATHS['logs']/ str(year)/ "AT_Process_Log.xlsx"


def copy_weekly_to_output(source: Path, year: int, month: int) -> Path:
    output_folfer = (PATHS['output'] / str(year) / f"{month:02d}")
    output_folfer.mkdir(parents=True, exist_ok=True)

    destination = output_folfer / source.name
    shutil.copy2(source, destination)
    return destination


def ensure_directories() -> None:
    for folder in PATHS.values():
        folder.mkdir(parents=True, exist_ok=True)

def output_exists(file_path: Path) -> bool:
    return file_path.exists()