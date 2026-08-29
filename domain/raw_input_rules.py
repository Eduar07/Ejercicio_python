"""
Business rules for identifying and pairing the two raw ActivTrak exports
(Productivity by User + User_Details) by the week they belong to.
Pure — no I/O, no openpyxl.
"""
from datetime import date, datetime, timedelta
from typing import Optional
import calendar 
from domain.errors import ATError

from domain.model import RawInputPair

import calendar

def parse_prod_by_user_filename(filename: str) -> tuple[date, date]:
    name_without_extension = filename.replace(".xlsx", "").strip()
    date_part = name_without_extension.split(" ")[-1]

    if "-" in date_part:
        start_text, end_text = date_part.split("-")
        week_start = datetime.strptime(start_text, "%Y_%m_%d").date()
        week_end = datetime.strptime(end_text, "%Y_%m_%d").date()

        if week_start.month != week_end.month:
            raise ATError(
                "ERR028",
                "Invalid file name. A partial cross-month file must stay within a single calendar month."
            )

        if week_start.weekday() == 0:
            # closing part: must end on the last day of the month
            last_day = calendar.monthrange(week_end.year, week_end.month)[1]
            if week_end.day != last_day:
                raise ATError(
                    "ERR028",
                    "Invalid file name. The closing-month partial file must end on the last day of the month."
                )
        elif week_end.weekday() == 4:
            # opening part: must start on the 1st of the month
            if week_start.day != 1:
                raise ATError(
                    "ERR028",
                    "Invalid file name. The opening-month partial file must start on the first day of the month."
                )
        else:
            raise ATError(
                "ERR028",
                "Invalid file name. The date range does not match a valid cross-month week pattern."
            )

    else:
        week_start = datetime.strptime(date_part, "%Y_%m_%d").date()

        if week_start.weekday() != 0:
            raise ATError(
                "ERR028",
                "Invalid file name. The date provided does not represent the start of the reporting week. "
                "Please use the Monday date for the week being processed."
            )

        week_end = week_start + timedelta(days=4)

    return week_start, week_end


def parse_user_details_filename(filename: str) -> date:
    """
    Example: "User_Details_2026-08-03" -> date(2026, 8, 3)
    """
    name_without_extension = filename.replace(".xlsx", "").strip()
    date_part = name_without_extension.split("_")[-1]
    return datetime.strptime(date_part, "%Y-%m-%d").date()


def find_matching_pair(filenames: list[str]) -> Optional[RawInputPair]:

    prod_by_user_files = [f for f in filenames if f.startswith("Productivity by User")]
    user_details_files = [f for f in filenames if f.startswith("User_Details")]

    if len(prod_by_user_files) != 1 or len(user_details_files) != 1:
        return None

    prod_filename = prod_by_user_files[0]
    details_filename = user_details_files[0]

    week_start, week_end = parse_prod_by_user_filename(prod_filename)
    details_date = parse_user_details_filename(details_filename)

    if week_start != details_date:
        return None

    return RawInputPair(
        prod_by_user_filename=prod_filename,
        user_details_filename=details_filename,
        week_start=week_start,
        week_end=week_end,
    )
