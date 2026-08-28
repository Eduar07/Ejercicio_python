from abc import ABC, abstractmethod

from domain.model import LogEntry


class ExecutionLogPort(ABC):
    @abstractmethod
    def write(self, log_entry: LogEntry) -> None:
        ...
