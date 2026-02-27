# vom/infrastructure/ssh_base.py

from abc import ABC, abstractmethod
from typing import Tuple


class BaseSSHClient(ABC):

    @abstractmethod
    def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Execute command on remote host.

        Returns:
            (exit_code, stdout, stderr)
        """
        pass

    @abstractmethod
    def close(self):
        pass