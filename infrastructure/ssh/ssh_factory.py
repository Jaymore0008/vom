# vom/infrastructure/ssh_factory.py

import os
import logging

from .ssh_base import BaseSSHClient
from .ssh_client import RealSSHClient
from .mock_ssh_client import MockSSHClient
from ..mocks.mock_data import MOCK_RESPONSES


def create_ssh_client(host: str, username: str = "root") -> BaseSSHClient:

    env = os.getenv("ENV", "PROD").upper()

    if env == "DEV":

        logging.info(f"[SSH Factory] Using MockSSHClient for {host}")

        return MockSSHClient(MOCK_RESPONSES)

    logging.info(f"[SSH Factory] Using RealSSHClient for {host}")

    return RealSSHClient(host=host, username=username)

