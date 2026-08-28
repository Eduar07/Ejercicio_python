from abc import ABC, abstractmethod
from typing import Optional

from domain.model import EmployeeMetric, RawInputPair


class RawInputPort(ABC):
    @abstractmethod
    def find_next_pair(self) -> Optional[RawInputPair]:
        ...

    @abstractmethod
    def read_employee_metrics(self, pair: RawInputPair) -> list[EmployeeMetric]:
        ...

    @abstractmethod
    def archive_pair(self, pair: RawInputPair) -> None:
        ...
