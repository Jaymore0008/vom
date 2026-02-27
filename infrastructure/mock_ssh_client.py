# vom/infrastructure/mock_ssh_client.py

from typing import Tuple
from .ssh_base import BaseSSHClient


class MockSSHClient(BaseSSHClient):

    def __init__(self, mock_data: dict):
        """
        mock_data = {
            "hagrp -state": "...output...",
            "vxprint -ht": "...output...",
        }
        """
        self.mock_data = mock_data

    def execute(self, command: str) -> Tuple[int, str, str]:

        if command in self.mock_data:
            return 0, self.mock_data[command], ""

        return 1, "", f"Command not mocked: {command}"

    def close(self):
        pass