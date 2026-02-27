# vom/application/cluster_service.py

import logging
from typing import Dict, List

from shared.config_loader import ConfigLoader
from infrastructure.veritas_client import VeritasClient

from domain.cluster import Cluster
from domain.node import Node
from domain.diskgroup import DiskGroup
from domain.volume import Volume
from domain.filesystem import Filesystem
from domain.service_group import ServiceGroup
from domain.issue import Issue


class ClusterService:

    def __init__(self):
        self.config = ConfigLoader()

    # --------------------------------------------------
    # Build complete cluster snapshot
    # --------------------------------------------------

    def build_cluster(self, sid: str) -> Cluster:

        sp_ip = self.config.get_sp(sid)
        sf_ip = self.config.get_sf(sid)

        logging.info(f"[ClusterService] Building cluster for SID={sid}")

        # Create clients
        sp_client = VeritasClient(sp_ip)
        sf_client = VeritasClient(sf_ip)

        # Detect node states
        sp_alive = sp_client.ping()
        sf_alive = sf_client.ping()

        active_node = None

        if sp_alive:
            active_node = sp_ip
        elif sf_alive:
            active_node = sf_ip

        # Build cluster object
        cluster = Cluster(
            sid=sid,
            sp_node=sp_ip,
            sf_node=sf_ip,
            active_node=active_node
        )

        # Add nodes
        cluster.nodes = [
            Node(
                name=f"{sid}-SP",
                ip=sp_ip,
                role="SP",
                state="RUNNING" if sp_alive else "OFFLINE",
                is_active=(sp_ip == active_node)
            ),
            Node(
                name=f"{sid}-SF",
                ip=sf_ip,
                role="SF",
                state="RUNNING" if sf_alive else "OFFLINE",
                is_active=(sf_ip == active_node)
            )
        ]

        # Collect data from both nodes
        self._collect_diskgroups(cluster, sp_client, sf_client)
        self._collect_volumes(cluster, sp_client, sf_client)
        self._collect_filesystems(cluster, sp_client, sf_client)
        self._collect_service_groups(cluster, sp_client, sf_client)

        # Detect issues
        cluster.detect_issues()

        # Cleanup
        sp_client.close()
        sf_client.close()

        return cluster

    # --------------------------------------------------
    # Diskgroups
    # --------------------------------------------------

    def _collect_diskgroups(self, cluster, sp_client, sf_client):

        dg_map = {}

        for client in [sp_client, sf_client]:

            try:
                diskgroups = client.get_diskgroups()

                for dg in diskgroups:

                    name = dg["name"]

                    if name not in dg_map:
                        dg_map[name] = DiskGroup(
                            name=name,
                            state=dg["state"],
                            node=client.host
                        )

            except Exception as e:
                logging.warning(
                    f"[ClusterService] Diskgroup fetch failed on {client.host}: {e}"
                )

        cluster.diskgroups = list(dg_map.values())

    # --------------------------------------------------
    # Volumes
    # --------------------------------------------------

    def _collect_volumes(self, cluster, sp_client, sf_client):

        volumes = []

        for client in [sp_client, sf_client]:

            try:
                data = client.get_volumes()

                for v in data:
                    volumes.append(
                        Volume(
                            name=v["volume"],
                            diskgroup=v["diskgroup"],
                            layout=v["layout"],
                            size_gb=v["size_gb"],
                            mount_point=v.get("mount"),
                            mounted=(v.get("status") == "Mounted"),
                            node=client.host
                        )
                    )

            except Exception as e:
                logging.warning(
                    f"[ClusterService] Volume fetch failed on {client.host}: {e}"
                )

        cluster.volumes = volumes

    # --------------------------------------------------
    # Filesystems
    # --------------------------------------------------

    def _collect_filesystems(self, cluster, sp_client, sf_client):

        filesystems = []

        for client in [sp_client, sf_client]:

            try:
                data = client.get_filesystems()

                for fs in data:
                    filesystems.append(
                        Filesystem(
                            device=fs["device"],
                            mount_point=fs["mount_point"],
                            size_gb=fs["size_gb"],
                            used_gb=fs["used_gb"],
                            available_gb=fs["available_gb"],
                            percent_used=fs["percent_used"],
                            node=client.host
                        )
                    )

            except Exception as e:
                logging.warning(
                    f"[ClusterService] Filesystem fetch failed on {client.host}: {e}"
                )

        cluster.filesystems = filesystems

    # --------------------------------------------------
    # Service Groups (UPDATED)
    # --------------------------------------------------

    def _collect_service_groups(self, cluster, sp_client, sf_client):

        sg_map = {}

        for client in [sp_client, sf_client]:

            try:
                print(f"Running hagrp on {client.host}")
                data = client.get_service_groups()
                print(data)

                for entry in data:

                    name = entry["service_group"]
                    node = entry["node"]
                    state = entry["state"]

                    if name not in sg_map:
                        sg_map[name] = ServiceGroup(name=name)

                    sg_map[name].set_state(node, state)

            except Exception as e:
                logging.warning(
                    f"[ClusterService] SG fetch failed on {client.host}: {e}"
                )

        cluster.service_groups = list(sg_map.values())

    # --------------------------------------------------
    # Public summary method
    # --------------------------------------------------

    def get_cluster_summary(self, sid: str):
        cluster = self.build_cluster(sid)
        return cluster.summary()

    # --------------------------------------------------
    # Get full cluster object
    # --------------------------------------------------

    def get_cluster(self, sid: str) -> Cluster:
        return self.build_cluster(sid)
