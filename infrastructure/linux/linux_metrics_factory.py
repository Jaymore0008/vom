# vom/infrastructure/linux_metrics_factory.py

import os

from .linux_metrics_client import LinuxMetricsClient
from .mock_linux_metrics_client import MockLinuxMetricsClient
from ..ssh.ssh_factory import create_ssh_client


def create_linux_metrics_client(host: str, username: str = "root"):

    env = os.getenv("ENV", "PROD")

    if env.upper() == "DEV":
        return MockLinuxMetricsClient(host)

    ssh = create_ssh_client(host, username)
    return LinuxMetricsClient(ssh, host)