import argparse
from datetime import datetime

from domain.model import LogEntry
from domain.errors import ATError

from infrastructure.graph_config import GraphCredentials

from adapters.key_vault_auth import get_key_vault_session, get_sharepoint_credentials
from adapters.graph_auth import get_access_token
from adapters.sharepoint_client import GraphContext, get_site_id, get_drive_id
from adapters.sharepoint_raw_input_adapter import SharePointRawInputAdapter
from adapters.sharepoint_master_employee_adapter import SharePointMasterEmployeeAdapter
from adapters.sharepoint_metrics_output_adapter import SharePointMetricsOutputAdapter
from adapters.sharepoint_log_adapter import SharePointExecutionLogAdapter

from application.process_weekly_metrics import process_weekly_metrics


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-name", required=True, help="Triggering file name (not used to decide what to read — script re-lists RawInputs itself)")
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
    site_id = get_site_id(access_token)
    drive_id = get_drive_id(access_token, site_id)

    return GraphContext(
        access_token=access_token,
        site_id=site_id,
        drive_id=drive_id,
    )


def main() -> None:
    args = parse_arguments()
    context = None
    pair = None

    try:
        access_token, credentials = authenticate_graph(args.client_secret)
        context = build_context(access_token)

        raw_input = SharePointRawInputAdapter(context)
        master_employees_reader = SharePointMasterEmployeeAdapter(context)
        metrics_output = SharePointMetricsOutputAdapter(context)

        pair = raw_input.find_next_pair()

        if pair is None:
            print("Raw pair not ready yet — waiting for the matching file.")
            return

        result = process_weekly_metrics(pair, raw_input, master_employees_reader, metrics_output)

        if result:
            print(result)

    except ATError as error:

        if error.code == "ERR015":
            status = "SUCCESS"
        elif error.code == "ERR013":
            status = "PENDING"
        else:
            status = "ERROR"

        source_name = pair.prod_by_user_filename if pair else "RawInputs (pair not found)"

        log_entry = LogEntry(
            source_file=source_name,
            execution_date=datetime.now(),
            status=status,
            error_message=error.detail,
            error_code=error.code,
        )

        if context is not None:
            SharePointExecutionLogAdapter(context).write(log_entry)
        else:
            print(f"Could not authenticate, cannot upload remote log: {error}")

        raise


if __name__ == "__main__":
    main()
