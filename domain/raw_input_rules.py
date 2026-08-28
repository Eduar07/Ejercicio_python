"""
Business rules for identifying and pairing the two raw ActivTrak exports
(Productivity by User + User_Details) by the week they belong to.
Pure — no I/O, no openpyxl.
"""
from datetime import date, datetime, timedelta
from typing import Optional

from domain.model import RawInputPair


def parse_prod_by_user_filename(filename: str) -> tuple[date, date]:
    """
    Normal week:   "Productivity by User 2026_08_03"
                   -> week_start = 2026-08-03, week_end = week_start + 4 days

    Partial week:  "Productivity by User 2026_05_29-2026_05_31"
                   -> week_start = 2026-05-29, week_end = 2026-05-31 (read directly)
    """
    name_without_extension = filename.replace(".xlsx", "").strip()
    date_part = name_without_extension.split(" ")[-1]

    if "-" in date_part:
        start_text, end_text = date_part.split("-")
        week_start = datetime.strptime(start_text, "%Y_%m_%d").date()
        week_end = datetime.strptime(end_text, "%Y_%m_%d").date()
    else:
        week_start = datetime.strptime(date_part, "%Y_%m_%d").date()
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
