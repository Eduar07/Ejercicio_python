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
    source_file: str = ""

@dataclass
class WeekData:
    week_start: date
    week_end: date
    year: int
    employees: list[EmployeeMetric]

@dataclass
class LogEntry:

    correlation_id: str
    source_file: str
    execution_date: datetime
    status: str
    records_processed: int
    error_message: str
    stage: str
    level: str
    error_code: str
    week_range: str
    duration_ms: int

@dataclass
class MasterEmployee:
    employee_id: str
    name: str
    email: str
    status: str