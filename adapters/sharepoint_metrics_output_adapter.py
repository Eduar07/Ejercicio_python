"""
Adapter implementing MetricsOutputPort against SharePoint (via Graph) for
the monthly output workbook (AT_Metrics_{year}-{month}.xlsx).
"""
import io
from datetime import date

import openpyxl

from domain.model import EmployeeMetric

from application.ports.metrics_output_port import MetricsOutputPort

from infrastructure.config import OUTPUT_SHEET_NAME

from adapters.sharepoint_client import GraphContext, get_file_by_path, upload_file_graph, build_output_path
from adapters.excel_write import (
    create_workbook,
    write_week_range,
    write_headers,
    write_employees,
    apply_column_colors,
    apply_header_font,
    set_column_width,
    apply_colors,
    apply_table_borders,
    get_next_block_start_row,
    find_week_block_start_row,
    is_placeholder_block,
    clear_employee_rows,
)


class SharePointMetricsOutputAdapter(MetricsOutputPort):
    def __init__(self, context: GraphContext):
        self._context = context

    def write_week(
        self,
        year: int,
        month: int,
        week_start: date,
        week_end: date,
        employees: list[EmployeeMetric],
    ) -> bool:
        folder, file_name = build_output_path(year, month)
        path = f"{folder}/{file_name}"

        existing_bytes = get_file_by_path(self._context, path)

        if existing_bytes is not None:
            workbook = openpyxl.load_workbook(existing_bytes)
            worksheet = workbook[OUTPUT_SHEET_NAME]
        else:
            workbook, worksheet = create_workbook()

        existing_start_row = find_week_block_start_row(worksheet, week_start, week_end)
        incoming_is_placeholder = employees[0].active_days is None if employees else False

        if existing_start_row is not None:
            # A block already exists for this week. Only one transition is allowed:
            # placeholder -> real (a cross-month template getting filled in by the
            # matching partial-week pair). Anything else — the template being
            # recreated, or real data already there — is a no-op; real data must
            # never be overwritten by a placeholder.
            if is_placeholder_block(worksheet, existing_start_row) and not incoming_is_placeholder:
                clear_employee_rows(worksheet, existing_start_row)
                start_row = existing_start_row
            else:
                return False
        else:
            start_row = get_next_block_start_row(worksheet)

            write_week_range(worksheet, week_start, week_end, start_row)
            write_headers(worksheet, start_row)
            apply_column_colors(worksheet, start_row)
            apply_header_font(worksheet, start_row)
            set_column_width(worksheet)

        write_employees(worksheet, employees, start_row)
        apply_colors(worksheet, employees, start_row)
        apply_table_borders(worksheet, employees, start_row)

        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        upload_file_graph(self._context, folder, file_name, buffer.getvalue())

        return True
