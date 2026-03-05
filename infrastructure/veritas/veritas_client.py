# vom/infrastructure/veritas_client.py

"""
VeritasClient

Execution layer responsible for:

- Executing Veritas CLI commands via SSHClient
- Parsing outputs via VeritasParser
- Returning structured domain objects
"""

import logging
from typing import List, Dict, Union, Any

from ..ssh.ssh_client import SSHCommandError, SSHConnectionError
from ..ssh.ssh_factory import create_ssh_client
from .parsers import VeritasParser
from .veritas_commands import VeritasCommands

from domain.storage.diskgroup import DiskGroup
from domain.storage.volume import Volume
from domain.storage.filesystem import Filesystem
from domain.cluster.service_group import ServiceGroup


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

    def _run(self, command: Union[str, VeritasCommands]) -> str:

        if isinstance(command, VeritasCommands):
            command = command.value

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

    def get_diskgroups(self) -> List[DiskGroup]:

        output = self._run(VeritasCommands.VXDG_LIST)

        return VeritasParser.parse_diskgroups(output)

    # --------------------------------------------------
    # Volumes
    # --------------------------------------------------

    def get_volumes(self) -> List[Volume]:

        vx_output = self._run(VeritasCommands.VXPRINT)
        df_output = self._run(VeritasCommands.DF)

        return VeritasParser.parse_volumes(
            vx_output,
            df_output
        )

    # --------------------------------------------------
    # Filesystems
    # --------------------------------------------------

    def get_filesystems(self) -> List[Filesystem]:

        df_output = self._run(VeritasCommands.DF)

        return VeritasParser.parse_filesystems(df_output)

    # --------------------------------------------------
    # Service Groups
    # --------------------------------------------------

    def get_service_groups(self) -> List[ServiceGroup]:

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

    def get_cluster_summary(self) -> Dict[str, Any]:

        df_output = self._run(VeritasCommands.DF)
        vx_output = self._run(VeritasCommands.VXPRINT)

        return {

            "host": self.host,

            "diskgroups": VeritasParser.parse_diskgroups(
                self._run(VeritasCommands.VXDG_LIST)
            ),

            "volumes": VeritasParser.parse_volumes(
                vx_output,
                df_output
            ),

            "filesystems": VeritasParser.parse_filesystems(
                df_output
            ),

            "service_groups": VeritasParser.parse_service_group_states(
                self._run(VeritasCommands.HAGRP_STATE)
            ),

            "resources": VeritasParser.parse_resource_states(
                self._run(VeritasCommands.HARES_STATE)
            ),

            "node_state": VeritasParser.parse_node_states(
                self._run(VeritasCommands.HASYS_STATE)
            )
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