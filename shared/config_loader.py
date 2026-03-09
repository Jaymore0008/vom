from pathlib import Path
import yaml


CONFIG_PATH = Path(__file__).parent.parent / "config" / "clusters.yaml"


class ConfigLoader:

    def __init__(self):

        self.config = self._load_config()
        self.clusters = self.config.get("clusters", {})

    # --------------------------------------------------
    # Load YAML configuration
    # --------------------------------------------------

    def _load_config(self):

        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Cluster config not found: {CONFIG_PATH}")

        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)

    # --------------------------------------------------
    # Get full cluster configuration
    # --------------------------------------------------

    def get_cluster(self, sid):

        cluster = self.clusters.get(sid)

        if not cluster:
            raise ValueError(f"Cluster '{sid}' not found in configuration")

        return {
            "sp": cluster.get("SP"),
            "sf": cluster.get("SF"),
            "username": cluster.get("username", "root")
        }

    # --------------------------------------------------
    # Get primary node
    # --------------------------------------------------

    def get_sp(self, sid):

        cluster = self.get_cluster(sid)
        return cluster["sp"]

    # --------------------------------------------------
    # Get failover node
    # --------------------------------------------------

    def get_sf(self, sid):

        cluster = self.get_cluster(sid)
        return cluster["sf"]

    # --------------------------------------------------
    # List all cluster SIDs
    # --------------------------------------------------

    def get_all_sids(self):

        return list(self.clusters.keys())

    # --------------------------------------------------
    # Get full configuration
    # --------------------------------------------------

    def get_all(self):

        return self.clusters
