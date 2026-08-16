from domain.model import WeekData, EmployeeMetric, MasterEmployee
import unicodedata
from datetime import date
from datetime import timedelta


from domain.constants import HOURS_PER_DAY_THRESHOLD, PASSIVE_HOURS_THRESHOLD,DEPARTMENT,GOALS


def normalize_name(name: str) -> str:
    name = name.strip().upper()
    name = unicodedata.normalize("NFD", name)
    name = "".join(char for char in name if unicodedata.category(char)!= "Mn"
    )
    return name

def calculate_productive_color(hours_per_day: float | str) -> str:
    if hours_per_day == "#N/A":
        return "none"
    if hours_per_day >= HOURS_PER_DAY_THRESHOLD:
        return "green"
    return "red"


def calculate_passive_status(passive_hours: float | str) -> str:
    if passive_hours == "#N/A":
        return "none"
    if passive_hours >= PASSIVE_HOURS_THRESHOLD:
        return "red"
    return "green"


def detect_cross_month(week_start: date, week_end: date) -> bool:
    if week_start.month != week_end.month:
        return True
    return False

def match_employees(weekly_employees: list[EmployeeMetric],
                    master_employess: list[MasterEmployee]) -> list[EmployeeMetric]:

    matched = []


    for employee in weekly_employees:

            employee_name = normalize_name(employee.name)

            for master in master_employess:
             master_name = normalize_name(master.name)

             if employee_name == master_name:
                 matched.append(employee)
                 break

    return matched


def apply_business_rules(
    employees: list[EmployeeMetric]) -> list[EmployeeMetric]:
    for employee in employees:

        employee.color_hours_day = calculate_productive_color(
            employee.hours_per_day
        )

        employee.color_passive = calculate_passive_status(
            employee.productive_passive_hours
        )

    return employees


def build_placeholder_employees(master_employees: list[MasterEmployee]) -> list[EmployeeMetric]:
    placeholders = []

    for master in master_employees:
        employee = EmployeeMetric(
            name=master.name,
            department=DEPARTMENT,
            productive_active_hours=None,
            productive_passive_hours=None,
            total_hours=None,
            active_days=None,
            goal=GOALS["weekly"],
            hours_per_day=None,
            comments="",
            source_file="",
        )
        placeholders.append(employee)

    return placeholders

from datetime import timedelta

def split_cross_month_range(
    week_start: date, week_end: date
) -> tuple[date, date, date, date]:
    next_month_first_day = date(week_end.year, week_end.month, 1)
    closing_end = next_month_first_day - timedelta(days=1)
    opening_start = next_month_first_day
    return week_start, closing_end, opening_start, week_end