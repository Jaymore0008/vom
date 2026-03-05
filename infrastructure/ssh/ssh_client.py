# vom/infrastructure/ssh_client.py

import paramiko
import logging
from typing import Optional

from .ssh_base import BaseSSHClient
from ..models.command_result import CommandResult


class SSHConnectionError(Exception):
    pass
 

class SSHCommandError(Exception):
    pass


class RealSSHClient(BaseSSHClient):

    def __init__(self, host: str, username: str = "root", timeout: int = 10):

        self.host = host
        self.username = username
        self.timeout = timeout
        self.client: Optional[paramiko.SSHClient] = None

    def _connect(self):

        try:

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                hostname=self.host,
                username=self.username,
                timeout=self.timeout
            )

            transport = client.get_transport()
            if transport:
                transport.set_keepalive(30)

            self.client = client

            logging.info(f"[SSH] Connected: {self.host}")

        except Exception as e:

            logging.error(f"[SSH] Connection failed: {self.host} : {e}")
            raise SSHConnectionError(str(e))

    def execute(self, command: str, timeout: Optional[int] = None) -> CommandResult:

        if not self.client:
            self._connect()

        try:

            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=timeout or self.timeout
            )

            exit_code = stdout.channel.recv_exit_status()

            output = stdout.read().decode()
            error = stderr.read().decode()

            return CommandResult(
                exit_code=exit_code,
                stdout=output,
                stderr=error
            )

        except Exception as e:

            logging.error(f"[SSH] Command failed on {self.host}: {e}")

            # reset connection
            self.close()

            raise SSHCommandError(str(e))

    def close(self):

        if self.client:
            self.client.close()
            self.client = None
