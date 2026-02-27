# vom/infrastructure/veritas_client.py

"""
VeritasClient

Execution layer responsible for:

- Executing Veritas CLI commands via SSHClient
- Parsing outputs via VeritasParser
- Returning structured data for domain layer
"""

import logging
from typing import List, Dict, Tuple

from .ssh_client import SSHClient, SSHCommandError, SSHConnectionError
from .veritas_commands import VeritasCommands
from .parsers import VeritasParser

from .ssh_factory import create_ssh_client


class VeritasClient:

    def __init__(self, host: str, username: str = "root"):

        self.host = host
        self.username = username

        self.ssh = create_ssh_client(
            host=self.host,
            username=self.username
        )

    # --------------------------------------------------
    # Core execution wrapper
    # --------------------------------------------------

    def _run(self, command: str) -> str:

        try:

            exit_code, output, error = self.ssh.execute(command)

            if exit_code != 0:
                logging.warning(
                    f"[VeritasClient] Command failed on {self.host}: "
                    f"{command} | {error}"
                )

            return output

        except (SSHCommandError, SSHConnectionError) as e:

            logging.error(
                f"[VeritasClient] SSH error on {self.host}: {e}"
            )

            raise

    # --------------------------------------------------
    # Diskgroups
    # --------------------------------------------------

    def get_diskgroups(self) -> List[Dict]:

        output = self._run(VeritasCommands.VXDG_LIST)

        return VeritasParser.parse_diskgroups(output)

    # --------------------------------------------------
    # Volumes
    # --------------------------------------------------

    def get_volumes(self) -> List[Dict]:

        vx_output = self._run(VeritasCommands.VXPRINT)

        df_output = self._run(VeritasCommands.DF)

        return VeritasParser.parse_volumes(
            vx_output,
            df_output
        )

    # --------------------------------------------------
    # Filesystems
    # --------------------------------------------------

    def get_filesystems(self) -> List[Dict]:

        df_output = self._run(VeritasCommands.DF)

        return VeritasParser.parse_filesystems(df_output)

    # --------------------------------------------------
    # Service Groups
    # --------------------------------------------------

    def get_service_groups(self) -> List[Dict]:

        output = self._run(VeritasCommands.HAGRP_STATE)

        return VeritasParser.parse_service_group_states(output)

    # --------------------------------------------------
    # Resources
    # --------------------------------------------------

    def get_resources(self) -> List[Dict]:

        output = self._run(VeritasCommands.HARES_STATE)

        return VeritasParser.parse_resource_states(output)

    # --------------------------------------------------
    # Node state
    # --------------------------------------------------

    def get_node_state(self) -> List[Dict]:

        output = self._run(VeritasCommands.HASYS_STATE)

        return VeritasParser.parse_node_states(output)

    # --------------------------------------------------
    # Cluster summary
    # --------------------------------------------------

    def get_cluster_summary(self) -> Dict:

        return {

            "host": self.host,

            "diskgroups": self.get_diskgroups(),

            "volumes": self.get_volumes(),

            "filesystems": self.get_filesystems(),

            "service_groups": self.get_service_groups(),

            "resources": self.get_resources(),

            "node_state": self.get_node_state()
        }

    # --------------------------------------------------
    # Health check
    # --------------------------------------------------

    def ping(self) -> bool:

        try:

            self._run(VeritasCommands.HOSTNAME)

            return True

        except Exception:

            return False

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    def close(self):

        if self.ssh:
            self.ssh.close()

    # --------------------------------------------------
    # Context manager support
    # --------------------------------------------------

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.close()
