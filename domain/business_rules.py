from domain.models import WeekData, EmployeeMetric, MasterEmployee
import unicodedata
from datetime import date
from domain.constants import HOURS_PER_DAY_THRESHOLD, PASSIVE_HOURS_THRESHOLD


def normalize_name(name: str) -> str:
    name = name.strip().upper()
    name = unicodedata.normalize("NFD", name)
    name = "".join(char for char in name if unicodedata.category(char)!= "Mn"
    )
    return name

def calculate_productive_color(hours_per_day: float) -> str:
    if hours_per_day >= HOURS_PER_DAY_THRESHOLD:
        return "green"
    return "red"


def calculate_passive_status(passive_hours: float) -> str:
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