# vom/infrastructure/mock_ssh_client.py

import logging
from typing import Dict

from .ssh_base import BaseSSHClient
from ..models.command_result import CommandResult


class MockSSHClient(BaseSSHClient):

    def __init__(self, mock_data: Dict[str, str]):
        """
        mock_data example:

        {
            "hagrp -state": "...output...",
            "vxprint -ht": "...output..."
        }
        """
        self.mock_data = mock_data

    def execute(self, command: str, timeout=None) -> CommandResult:

        if command in self.mock_data:

            return CommandResult(
                exit_code=0,
                stdout=self.mock_data[command],
                stderr=""
            )

        logging.warning(f"[MockSSH] Command not mocked: {command}")

        return CommandResult(
            exit_code=1,
            stdout="",
            stderr=f"Command not mocked: {command}"
        )

    def close(self):
        pass