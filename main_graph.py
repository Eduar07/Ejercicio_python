import argparse
import io
import openpyxl
from datetime import datetime

from infrastructure.graph_config import GraphCredentials, BASE_FOLDER
from adapters.key_vault_auth import get_key_vault_session, get_sharepoint_credentials
from adapters.graph_auth import get_access_token

from adapters.sharepoint_client import (
    GraphContext,
    get_site_id,
    get_drive_id,
    list_input_files_graph,
    download_file_graph,
    upload_file_graph,
    get_file_by_path,
    build_output_path,
)
from adapters.excel_reader import read_weekly_excel, read_excel
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
    week_already_exists,
)
from application.process_weekly_metrics_remote import process_metric_remote
from domain.errors import ATError
from domain.model import LogEntry
from adapters.logger import write_log_entry_remote
from infrastructure.config import OUTPUT_SHEET_NAME


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--file-name", required=True, help="Weekly file name to process")
    parser.add_argument("--client-secret", required=True, help="Key Vault client secret")

    return parser.parse_args()


def authenticate_graph(vault_client_secret: str) -> tuple[str, GraphCredentials]:
    session = get_key_vault_session(vault_client_secret)
    credentials = get_sharepoint_credentials(session)

    access_token = get_access_token(
        credentials.tenant_id,
        credentials.client_id,
        credentials.client_secret,
    )

    return access_token, credentials


def build_context(access_token: str) -> GraphContext:
    # site_id identifies the SharePoint site itself (VMC-RPA), resolved from
    # its hostname + site path. drive_id identifies the specific document
    # library ("Shared Documents") inside that site, since a site can host
    # more than one drive. Both are required by every Graph API call below.
    # BASE_FOLDER ("Development/IT/AT_Internal_Metrics") is the folder path
    # *within* that drive where all Input/Output/Parametric Files live, so
    # every folder/file path used later is built as f"{BASE_FOLDER}/...".
    site_id = get_site_id(access_token)
    drive_id = get_drive_id(access_token, site_id)

    return GraphContext(
        access_token=access_token,
        site_id=site_id,
        drive_id=drive_id,
    )


def main() -> None:

    args = parse_arguments()

    try:
        access_token, credentials = authenticate_graph(args.client_secret)

        context = build_context(access_token)

        input_files = list_input_files_graph(context, f"{BASE_FOLDER}/Input")
        matching = [f for f in input_files if f["name"] == args.file_name]

        if not matching:
            raise ATError("ERR001", f"File {args.file_name} not found in Input")

        item_id = matching[0]["id"]

        weekly_bytes = download_file_graph(context, item_id)
        week_data = read_weekly_excel(weekly_bytes)

        master_bytes = get_file_by_path(
            context, f"{BASE_FOLDER}/Parametric Files/AT_Employees.xlsx"
        )
        master_employees = read_excel(master_bytes)

        week_data = process_metric_remote(context, week_data, master_employees)

        month_folder, month_file_name = build_output_path(
            week_data.week_start.year, week_data.week_start.month
        )

        month_path = f"{month_folder}/{month_file_name}"

        existing_bytes = get_file_by_path(context, month_path)

        if existing_bytes is not None:
            workbook = openpyxl.load_workbook(existing_bytes)
            worksheet = workbook[OUTPUT_SHEET_NAME]
        else:
            workbook, worksheet = create_workbook()

        if week_already_exists(worksheet, week_data.week_start, week_data.week_end):
            print("Week already exists. Nothing to process.")
            return

        start_row = get_next_block_start_row(worksheet)

        write_week_range(worksheet, week_data.week_start, week_data.week_end, start_row)
        write_headers(worksheet, start_row)
        apply_column_colors(worksheet, start_row)
        apply_header_font(worksheet, start_row)
        set_column_width(worksheet)
        write_employees(worksheet, week_data.employees, start_row)
        apply_colors(worksheet, week_data.employees, start_row)
        apply_table_borders(worksheet, week_data.employees, start_row)

        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        upload_file_graph(context, month_folder, month_file_name, buffer.getvalue())

    except ATError as error:

        if error.code == "ERR015":
            status = "SUCCESS"
        elif error.code == "ERR013":
            status = "PENDING"
        else:
            status = "ERROR"

        log_entry = LogEntry(
            source_file=args.file_name,
            execution_date=datetime.now(),
            status=status,
            error_message=error.detail,
            error_code=error.code,
        )

        write_log_entry_remote(context, log_entry)

        raise


if __name__ == "__main__":
    main()