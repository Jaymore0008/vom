# vom/infrastructure/ssh_factory.py

import os

from .ssh_client import RealSSHClient
from .mock_ssh_client import MockSSHClient
from .mock_data import MOCK_RESPONSES


def create_ssh_client(host: str, username: str = "root"):

    env = os.getenv("ENV", "PROD")

    if env.upper() == "DEV":
        return MockSSHClient(MOCK_RESPONSES)

    return RealSSHClient(host=host, username=username)

