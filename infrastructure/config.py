'''
Stores numbers and names that may change
'''

DATE_FORMAT = "%m/%d/%Y"

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


SHEET_MASTER = "Employees"
OUTPUT_SHEET_NAME = "Productive + Passive"
HEADER_ROW_MASTER = 1
START_ROW_MASTER = 2
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


# --- Raw ActivTrak files config ---

RAW_HEADER_ROW = 1
RAW_START_ROW = 2

PROD_BY_USER_COLUMNS_NEEDED = ["User", "ProdActive (secs)", "ProdPassive (secs)"]
USER_DETAILS_COLUMNS_NEEDED = ["User", "Active Days"]

RAW_INPUTS_FOLDER = "Input"
RAW_INPUTS_PROCESSED_FOLDER = "Input/Processed"
