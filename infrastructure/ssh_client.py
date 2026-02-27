# vom/infrastructure/ssh_client.py

import paramiko
import logging
import socket
import threading
import time


class SSHConnectionError(Exception):
    pass


class SSHCommandError(Exception):
    pass


class SSHClient:

    def __init__(
        self,
        host: str,
        username: str = "root",
        timeout: int = 10,
        retries: int = 2
    ):

        self.host = host
        self.username = username
        self.timeout = timeout
        self.retries = retries

        self.client = None

        self._lock = threading.Lock()

    # --------------------------------------------------
    # Connect
    # --------------------------------------------------

    def connect(self):

        with self._lock:

            if self.client:
                return

            try:

                client = paramiko.SSHClient()

                client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy()
                )

                client.connect(
                    hostname=self.host,
                    username=self.username,
                    timeout=self.timeout,
                    banner_timeout=self.timeout,
                    auth_timeout=self.timeout
                )

                self.client = client

                logging.info(f"[SSH] Connected → {self.host}")

            except (socket.timeout, paramiko.SSHException, Exception) as e:

                logging.error(f"[SSH] Connection failed → {self.host}: {e}")

                raise SSHConnectionError(
                    f"Failed to connect to {self.host}"
                ) from e

    # --------------------------------------------------
    # Execute command
    # --------------------------------------------------

    def execute(self, command: str):

        last_exception = None

        for attempt in range(self.retries + 1):

            try:

                if not self.client:
                    self.connect()

                logging.debug(
                    f"[SSH] Executing on {self.host}: {command}"
                )

                stdin, stdout, stderr = self.client.exec_command(
                    command,
                    timeout=self.timeout
                )

                exit_code = stdout.channel.recv_exit_status()

                output = stdout.read().decode(errors="ignore")

                error = stderr.read().decode(errors="ignore")

                if exit_code != 0:

                    logging.warning(
                        f"[SSH] Command failed ({self.host}): {command} | {error}"
                    )

                return exit_code, output, error

            except (
                paramiko.SSHException,
                socket.timeout,
                EOFError,
                Exception
            ) as e:

                logging.warning(
                    f"[SSH] Command attempt {attempt+1} failed → {self.host}: {e}"
                )

                last_exception = e

                self._reconnect()

                time.sleep(1)

        raise SSHCommandError(
            f"Command failed after retries on {self.host}: {command}"
        ) from last_exception

    # --------------------------------------------------
    # Reconnect logic
    # --------------------------------------------------

    def _reconnect(self):

        logging.info(f"[SSH] Reconnecting → {self.host}")

        self.close()

        self.connect()

    # --------------------------------------------------
    # Close connection
    # --------------------------------------------------

    def close(self):

        with self._lock:

            if self.client:

                try:
                    self.client.close()
                except Exception:
                    pass

                self.client = None

                logging.info(f"[SSH] Closed → {self.host}")

    # --------------------------------------------------
    # Context manager support
    # --------------------------------------------------

    def __enter__(self):

        self.connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.close()
