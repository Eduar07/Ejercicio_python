'''
Defines the shape of the data
'''

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class EmployeeMetric:
    name: str
    department: str
    productive_active_hours: float
    productive_passive_hours: float
    total_hours: float
    active_days: int
    goal: float
    hours_per_day: float
    comments: str
    color_hours_day: str = ""
    color_passive: str = ""
    color_active_hrs: str = ""
    color_total_hours: str = ""
    source_file: str = ""

@dataclass
class WeekData:
    week_start: date
    week_end: date
    year: int
    employees: list[EmployeeMetric]

@dataclass
class LogEntry:
    source_file: str
    execution_date: datetime
    status: str
    error_message: str
    error_code: str

@dataclass
class MasterEmployee:
    employee_id: str
    name: str
    email: str
    status: str

@dataclass
class RawInputPair:
    prod_by_user_filename: str
    user_details_filename: str
    week_start: date
    week_end: date