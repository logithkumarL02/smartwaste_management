from abc import ABC, abstractmethod
from typing import Tuple

class SortingDevice(ABC):
    """Abstract sorting device. All hardware implementations must implement this."""

    @abstractmethod
    def sort(self, command: str) -> Tuple[bool, str]:
        """Execute a sorting command. Returns (success, message)."""
        ...

    @abstractmethod
    def get_mode(self) -> str:
        """Return a string identifier for this hardware mode."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the device is connected and ready."""
        ...
