# vom/application/collectors/veritas_collector.py

"""
VeritasCollector

Responsible for collecting all Veritas cluster data and constructing
a fully populated Cluster domain object.

Responsibilities:
- Execute commands through VeritasClient
- Parse outputs
- Build domain objects
- Return Cluster object
"""

import logging
from typing import List

from domain.cluster.cluster import Cluster
from domain.cluster.node import Node
from domain.storage.diskgroup import DiskGroup
from domain.storage.volume import Volume
from domain.storage.filesystem import Filesystem
from domain.cluster.service_group import ServiceGroup

from infrastructure.veritas.veritas_client import VeritasClient


class VeritasCollector:

    def __init__(self, host: str, username: str = "root"):

        self.host = host
        self.username = username

    # --------------------------------------------------
    # Main collection entrypoint
    # --------------------------------------------------

    def collect_cluster(self, sid: str) -> Cluster:

        logging.info(f"[VeritasCollector] Collecting cluster data from {self.host}")

        with VeritasClient(self.host, self.username) as client:

            diskgroups = self._collect_diskgroups(client)
            volumes = self._collect_volumes(client)
            filesystems = self._collect_filesystems(client)
            service_groups = self._collect_service_groups(client)
            nodes = self._collect_nodes(client)

        cluster = Cluster(
            sid=sid,
            nodes=nodes,
            diskgroups=diskgroups,
            volumes=volumes,
            filesystems=filesystems,
            service_groups=service_groups
        )

        # Run domain health checks
        cluster.detect_issues()

        return cluster

    # --------------------------------------------------
    # Diskgroups
    # --------------------------------------------------

    def _collect_diskgroups(self, client: VeritasClient) -> List[DiskGroup]:

        try:

            diskgroups = client.get_diskgroups()

            logging.info(f"[VeritasCollector] Found {len(diskgroups)} diskgroups")

            return diskgroups

        except Exception as e:

            logging.error(f"[VeritasCollector] Diskgroup collection failed: {e}")

            return []

    # --------------------------------------------------
    # Volumes
    # --------------------------------------------------

    def _collect_volumes(self, client: VeritasClient) -> List[Volume]:

        try:

            volumes = client.get_volumes()

            logging.info(f"[VeritasCollector] Found {len(volumes)} volumes")

            return volumes

        except Exception as e:

            logging.error(f"[VeritasCollector] Volume collection failed: {e}")

            return []

    # --------------------------------------------------
    # Filesystems
    # --------------------------------------------------

    def _collect_filesystems(self, client: VeritasClient) -> List[Filesystem]:

        try:

            filesystems = client.get_filesystems()

            logging.info(f"[VeritasCollector] Found {len(filesystems)} filesystems")

            return filesystems

        except Exception as e:

            logging.error(f"[VeritasCollector] Filesystem collection failed: {e}")

            return []

    # --------------------------------------------------
    # Service Groups
    # --------------------------------------------------

    def _collect_service_groups(self, client: VeritasClient) -> List[ServiceGroup]:

        try:

            service_groups = client.get_service_groups()

            logging.info(f"[VeritasCollector] Found {len(service_groups)} service groups")

            return service_groups

        except Exception as e:

            logging.error(f"[VeritasCollector] Service group collection failed: {e}")

            return []

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------

    def _collect_nodes(self, client: VeritasClient) -> List[Node]:

        try:

            node_data = client.get_node_state()

            nodes = []

            for item in node_data:

                nodes.append(
                    Node(
                        name=item.get("node"),
                        ip=item.get("ip", ""),
                        role=item.get("role", "UNKNOWN"),
                        state=item.get("state", "UNKNOWN"),
                        is_active=item.get("is_active", False)
                    )
                )

            logging.info(f"[VeritasCollector] Found {len(nodes)} nodes")

            return nodes

        except Exception as e:

            logging.error(f"[VeritasCollector] Node collection failed: {e}")

            return []