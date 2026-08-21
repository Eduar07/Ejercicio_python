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

DATE_FORMAT = "%m/%d/%Y"

WEEKLY_COLUMNS = [
    "Name",
    "Department",
    "Productive Active Hrs",
    "Productive passive Hrs",
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
    "yellow": "ffd555"
}

STATUSES = {
    "success": "SUCCESS",
    "error": "ERROR",
    "warning": "WARNING",
    "pending": "PENDING"
}


SHEET_NAME = "Prod + Pass Hours All Dept"
SHEET_MASTER = "Employees"
OUTPUT_SHEET_NAME = "Productive + Passive"
HEADER_ROW = 3
START_ROW = 4
HEADER_ROW_MASTER = 1
START_ROW_MASTER = 2
WEEK_ROW = 2
OUTPUT_START_ROW = 7
PASSIVE_COLUMN = 4
HOURS_DAY_COLUMN = 8
PRODUCTIVE_ACTIVE_COLUMN = 3
TOTAL_PRODUCTIVE_COLUMN = 5
NAME_COLUMN = 1
DEPARTMENT_COLUMN = 2
ACTIVE_DAYS_COLUMN = 6
GOAL_COLUMN = 7
COMMENTS_COLUMN = 9
WEEK_ROW_OUTPUT = 5

YELLOW_COLUMNS = {GOAL_COLUMN, COMMENTS_COLUMN}
BOLD_BLACK_COLUMNS = {NAME_COLUMN, DEPARTMENT_COLUMN}


COLUMN_WIDTHS = {
    NAME_COLUMN:27,
    DEPARTMENT_COLUMN: 32,
    PRODUCTIVE_ACTIVE_COLUMN: 20,
    PASSIVE_COLUMN: 20,
    TOTAL_PRODUCTIVE_COLUMN: 20,
    ACTIVE_DAYS_COLUMN: 11,
    GOAL_COLUMN: 8,
    HOURS_DAY_COLUMN: 20,
    COMMENTS_COLUMN: 42,
}

LOG_COLUMNS = [
    "Source File",
    "Execution Date",
    "Status",
    "Error Message",
    "Error Code",
]

BLUE_FILL_COLOR = "4472C4"
YELLOW_FILL_COLOR = "ffd555"

HEADER_ROW_OUTPUT = 6