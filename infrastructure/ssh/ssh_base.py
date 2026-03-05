# vom/infrastructure/ssh_base.py

from abc import ABC, abstractmethod
from typing import Optional

from ..models.command_result import CommandResult


class BaseSSHClient(ABC):

    @abstractmethod
    def execute(self, command: str, timeout: Optional[int] = None) -> CommandResult:
        """
        Execute command on remote host.

        Returns:
            CommandResult(exit_code, stdout, stderr)
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close SSH connection"""
        pass