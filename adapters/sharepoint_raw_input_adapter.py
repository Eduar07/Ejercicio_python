"""
Adapter implementing RawInputPort against SharePoint (via Graph) for the
two raw ActivTrak exports (Productivity by User + User_Details).
"""
import io
from typing import Optional

from domain.model import EmployeeMetric, RawInputPair
from domain.raw_input_rules import find_matching_pair

from application.ports.raw_input_port import RawInputPort

from infrastructure.graph_config import BASE_FOLDER
from infrastructure.config import RAW_INPUTS_FOLDER

from adapters.sharepoint_client import (
    GraphContext,
    list_input_files_graph,
    download_file_graph,
    upload_file_graph,
    delete_file_graph,
    build_processed_path,
)
from adapters.excel_reader_raw import build_employee_metrics_from_raw


class SharePointRawInputAdapter(RawInputPort):
    def __init__(self, context: GraphContext):
        self._context = context
        self._items_by_name: dict[str, dict] = {}
        self._downloaded_by_pair: dict[tuple[str, str], tuple[io.BytesIO, io.BytesIO]] = {}

    def find_next_pair(self) -> Optional[RawInputPair]:
        raw_files = list_input_files_graph(self._context, f"{BASE_FOLDER}/{RAW_INPUTS_FOLDER}")
        self._items_by_name = {f["name"]: f for f in raw_files}

        return find_matching_pair(list(self._items_by_name.keys()))

    def read_employee_metrics(self, pair: RawInputPair) -> list[EmployeeMetric]:
        prod_item = self._items_by_name[pair.prod_by_user_filename]
        details_item = self._items_by_name[pair.user_details_filename]

        prod_bytes = download_file_graph(self._context, prod_item["id"])
        details_bytes = download_file_graph(self._context, details_item["id"])

        self._downloaded_by_pair[self._key(pair)] = (prod_bytes, details_bytes)

        return build_employee_metrics_from_raw(
            prod_bytes, details_bytes, source_file=pair.prod_by_user_filename
        )

    def archive_pair(self, pair: RawInputPair) -> None:
        prod_bytes, details_bytes = self._downloaded_by_pair[self._key(pair)]

        processed_folder = build_processed_path(pair.week_start.year, pair.week_start.month)

        upload_file_graph(self._context, processed_folder, pair.prod_by_user_filename, prod_bytes.getvalue())
        upload_file_graph(self._context, processed_folder, pair.user_details_filename, details_bytes.getvalue())

        delete_file_graph(self._context, f"{BASE_FOLDER}/{RAW_INPUTS_FOLDER}", pair.prod_by_user_filename)
        delete_file_graph(self._context, f"{BASE_FOLDER}/{RAW_INPUTS_FOLDER}", pair.user_details_filename)

    def _key(self, pair: RawInputPair) -> tuple[str, str]:
        return (pair.prod_by_user_filename, pair.user_details_filename)
