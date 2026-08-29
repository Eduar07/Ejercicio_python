"""
Application layer orchestrator for the weekly metrics use case.
Depends only on domain + ports — no adapter or infrastructure imports.
"""
from domain.model import WeekData, RawInputPair
from domain.errors import ATError

from domain.business_rules import (
    match_employees,
    apply_business_rules,
    detect_cross_month,
    build_placeholder_employees,
    split_cross_month_range,
)

from application.ports.raw_input_port import RawInputPort
from application.ports.master_employee_port import MasterEmployeePort
from application.ports.metrics_output_port import MetricsOutputPort


def process_weekly_metrics(
    pair: RawInputPair,
    raw_input: RawInputPort,
    master_employees_reader: MasterEmployeePort,
    metrics_output: MetricsOutputPort,
) -> str | None:
    """
    Runs the full weekly metrics flow for an already-identified raw pair:
    read raw hours, match against the master list, apply business rules,
    write the week block to the monthly output, and archive the raw files.

    Returns a status message when there's nothing to do (week already
    written); returns None on a normal successful write. Raises ATError
    (ERR013/ERR015) when the week crosses two months.
    """
    employees = raw_input.read_employee_metrics(pair)

    week_data = WeekData(
        week_start=pair.week_start,
        week_end=pair.week_end,
        year=pair.week_start.year,
        employees=employees,
    )

    master_employees = master_employees_reader.get_master_employees()

    cross_month = detect_cross_month(week_data.week_start, week_data.week_end)

    if cross_month:
        placeholders = build_placeholder_employees(master_employees)

        closing_start, closing_end, opening_start, opening_end = split_cross_month_range(
            week_data.week_start, week_data.week_end
        )

        written_closing = metrics_output.write_week(
            closing_start.year, closing_start.month, closing_start, closing_end, placeholders
        )
        written_opening = metrics_output.write_week(
            opening_start.year, opening_start.month, opening_start, opening_end, placeholders
        )

        # El par sin partir ya cumplió su función (detectar el cruce); se archiva acá
        # para no bloquear find_next_pair() cuando lleguen los pares parciales que van
        # a completar estas plantillas (ver sharepoint_metrics_output_adapter.write_week).
        raw_input.archive_pair(pair)

        if written_closing or written_opening:
            raise ATError(
                "ERR013",
                "The weekly file crosses two months — templates created for manual completion"
            )
        else:
            raise ATError(
                "ERR015",
                "The weekly file crosses two months — templates already existed, nothing changed"
            )

    matched_employees = match_employees(week_data.employees, master_employees)
    week_data.employees = apply_business_rules(matched_employees)

    written = metrics_output.write_week(
        week_data.week_start.year,
        week_data.week_start.month,
        week_data.week_start,
        week_data.week_end,
        week_data.employees,
    )

    raw_input.archive_pair(pair)

    if not written:
        return "Week already exists. Nothing to process."

    return None
