"""
Adapter for writing execution logs to a yearly Excel log file.
"""

from pathlib import Path
import openpyxl
from openpyxl import Workbook

from domain.model import LogEntry
from adapters.storage import get_log_path
from infrastructure.config import LOG_COLUMNS

def write_log_entry(log_entry: LogEntry) -> None:

    log_path = get_log_path(log_entry.execution_date.year)

    if log_path.exists():
        workbook = openpyxl.load_workbook(log_path)
        worksheet = workbook.active
    else:
        workbook = Workbook()
        worksheet = workbook.active

        for column, header in enumerate(LOG_COLUMNS, start=1):
            worksheet.cell(row=1, column=column, value=header)

    next_row = worksheet.max_row + 1

    values = [
        log_entry.source_file,
        log_entry.execution_date.strftime("%Y-%m-%d %H:%M:%S"),
        log_entry.status,
        log_entry.error_message,
        log_entry.error_code,
    ]

    for column, value in enumerate(values, start=1):
        worksheet.cell(row=next_row, column=column, value=value)

    workbook.save(log_path)