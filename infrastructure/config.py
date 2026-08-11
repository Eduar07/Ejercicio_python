'''
Stores numbers and names that may change
from pathlib import Path
Path is the class.
Path("data") is an instance of that class (the object created).
route is the variable that stores that instance.
"data" is not "the object", it is an argument (string) you pass to the constructor.
'''

from pathlib import Path
'''config, input arguments'''
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

OUTPUT_COLUMNS = [
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
OUTPUT_SHEET_NAME = "Productive + Passive"