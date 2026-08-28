"""
Adapter implementing MasterEmployeePort against SharePoint (via Graph)
for the AT_Employees.xlsx master file.
"""
from domain.model import MasterEmployee
from domain.errors import ATError

from application.ports.master_employee_port import MasterEmployeePort

from infrastructure.graph_config import BASE_FOLDER

from adapters.sharepoint_client import GraphContext, get_file_by_path
from adapters.excel_reader import read_excel

MASTER_EMPLOYEES_PATH = f"{BASE_FOLDER}/Parametric Files/AT_Employees.xlsx"


class SharePointMasterEmployeeAdapter(MasterEmployeePort):
    def __init__(self, context: GraphContext):
        self._context = context

    def get_master_employees(self) -> list[MasterEmployee]:
        master_bytes = get_file_by_path(self._context, MASTER_EMPLOYEES_PATH)

        if master_bytes is None:
            raise ATError("ERR025", f"File {MASTER_EMPLOYEES_PATH} not found")

        return read_excel(master_bytes)
