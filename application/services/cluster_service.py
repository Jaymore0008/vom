# vom/application/services/cluster_service.py

"""
ClusterService

Application service responsible for cluster-related use cases.

Responsibilities:
- orchestrate cluster data collection
- run domain health checks
- expose cluster summaries for UI/API
"""

import logging
from typing import Optional

from domain.cluster.cluster import Cluster
from application.collectors.veritas_collector import VeritasCollector
from shared.config_loader import ConfigLoader


class ClusterService:

    def __init__(self):

        self.config = ConfigLoader()

    # --------------------------------------------------
    # Collect cluster from configured host
    # --------------------------------------------------

    def collect_cluster(self, sid: str) -> Optional[Cluster]:

        try:

            cluster_config = self.config.get_cluster(sid)

            sp = cluster_config["sp"]
            sf = cluster_config["sf"]
            username = cluster_config.get("username", "root")

            # Try primary node first
            try:

                collector = VeritasCollector(sp, username)

                cluster = collector.collect_cluster(sid)

                logging.info(f"[ClusterService] Cluster {sid} collected from SP {sp}")

                return cluster

            except Exception as e:

                logging.warning(
                    f"[ClusterService] SP node unreachable for {sid} ({sp}). "
                    f"Trying SF {sf}. Error: {e}"
                )

            # Try failover node
            collector = VeritasCollector(sf, username)

            cluster = collector.collect_cluster(sid)

            logging.info(f"[ClusterService] Cluster {sid} collected from SF {sf}")

            return cluster

        except Exception as e:

            logging.error(f"[ClusterService] Failed to collect cluster {sid}: {e}")

            return None

    # --------------------------------------------------
    # Get cluster summary (for dashboards)
    # --------------------------------------------------
   
    def get_cluster_summary(self, sid: str) -> Optional[dict]:

        cluster = self.collect_cluster(sid)

        if not cluster:
            return None

        return cluster.summary()

    # --------------------------------------------------
    # Get cluster issues
    # --------------------------------------------------

    def get_cluster_issues(self, sid: str):

        cluster = self.collect_cluster(sid)

        if not cluster:
            return []

        return cluster.issues

    # --------------------------------------------------
    # Get cluster health
    # --------------------------------------------------

    def get_cluster_health(self, sid: str):

        cluster = self.collect_cluster(sid)
        
        if not cluster:
            return "UNKNOWN"

        #return cluster.health().value
        return cluster.health.value