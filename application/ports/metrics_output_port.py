from abc import ABC, abstractmethod
from datetime import date

from domain.model import EmployeeMetric


class MetricsOutputPort(ABC):
    @abstractmethod
    def write_week(
        self,
        year: int,
        month: int,
        week_start: date,
        week_end: date,
        employees: list[EmployeeMetric],
    ) -> bool:
        """Writes a week block into the given month's output workbook.
        Returns False (no-op) if that week already exists, True if written."""
        ...
