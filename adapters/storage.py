import shutil
from pathlib import Path

from domain.errors import ATError
from infrastructure.config import PATHS


def list_input_files() -> list[Path]:
    input_folder = PATHS["input"]

    if not input_folder.exists():
        raise ATError(
            "ERR001",
            f"Folder {input_folder} does not exist",
        )

    input_files = list(
        input_folder.glob("*.xlsx")
    )

    if not input_files:
        raise ATError(
            "ERR002",
            "No Excel files to process",
        )

    return input_files


def get_employees_path() -> Path:
    return (
        PATHS["parametric"]
        / "AT_Employees.xlsx"
    )


def get_output_path(
    year: int,
    month: int,
) -> Path:

    output_folder = (
        PATHS["output"]
        / str(year)
        / f"{month:02d}"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        output_folder
        / f"AT_Metrics_{year}-{month:02d}.xlsx"
    )


def get_log_path(year: int) -> Path:
    log_folder = (
        PATHS["logs"]
        / str(year)
    )

    log_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        log_folder
        / "AT_Process_Log.xlsx"
    )


def copy_weekly_to_output(
    source: Path,
    year: int,
    month: int,
) -> Path:

    output_folder = (
        PATHS["output"]
        / str(year)
        / f"{month:02d}"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        output_folder
        / source.name
    )

    shutil.copy2(
        source,
        destination,
    )

    return destination


def ensure_directories() -> None:
    for folder in PATHS.values():
        folder.mkdir(
            parents=True,
            exist_ok=True,
        )


def output_exists(
    file_path: Path,
) -> bool:
    return file_path.exists()


def get_next_month_output_path(
    year: int,
    month: int,
) -> Path:

    next_year = year
    next_month = month + 1

    if next_month == 13:
        next_month = 1
        next_year += 1

    output_folder = (
        PATHS["output"]
        / str(next_year)
        / f"{next_month:02d}"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        output_folder
        / f"AT_Metrics_"
        f"{next_year}-{next_month:02d}.xlsx"
    )