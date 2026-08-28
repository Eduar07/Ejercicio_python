from abc import ABC, abstractmethod

from domain.model import MasterEmployee


class MasterEmployeePort(ABC):
    @abstractmethod
    def get_master_employees(self) -> list[MasterEmployee]:
        ...
