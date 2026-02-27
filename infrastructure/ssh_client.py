# vom/infrastructure/ssh_client.py

import paramiko
import logging
from typing import Tuple

from .ssh_base import BaseSSHClient


class SSHConnectionError(Exception):
    pass


class SSHCommandError(Exception):
    pass


class RealSSHClient(BaseSSHClient):

    def __init__(self, host: str, username: str = "root", timeout: int = 10):

        self.host = host
        self.username = username
        self.timeout = timeout
        self.client = None

    def _connect(self):

        try:

            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(
                paramiko.AutoAddPolicy()
            )

            self.client.connect(
                hostname=self.host,
                username=self.username,
                timeout=self.timeout
            )

            logging.info(f"[SSH] Connected: {self.host}")

        except Exception as e:
            logging.error(f"[SSH] Connection failed: {self.host} : {e}")
            raise SSHConnectionError(str(e))

    def execute(self, command: str) -> Tuple[int, str, str]:

        if not self.client:
            self._connect()

        try:

            stdin, stdout, stderr = self.client.exec_command(command)

            exit_code = stdout.channel.recv_exit_status()

            output = stdout.read().decode()
            error = stderr.read().decode()

            return exit_code, output, error

        except Exception as e:
            raise SSHCommandError(str(e))

    def close(self):

        if self.client:
            self.client.close()
            self.client = None
