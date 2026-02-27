from pathlib import Path


CONFIG_PATH = Path(__file__).parent.parent / "config" / "sap_nodes.txt"


class ConfigLoader:

    def __init__(self):
        self.nodes = self._load_nodes()

    def _load_nodes(self):

        nodes = {}

        with open(CONFIG_PATH) as f:

            for line in f:

                if not line.strip():
                    continue

                if line.startswith("SID"):
                    continue

                parts = line.split()

                sid = parts[0]
                sp = parts[1]
                sf = parts[2]

                nodes[sid] = {
                    "sp": sp,
                    "sf": sf
                }

        return nodes

    def get_all_sids(self):

        return list(self.nodes.keys())

    def get_sp(self, sid):

        return self.nodes[sid]["sp"]

    def get_sf(self, sid):

        return self.nodes[sid]["sf"]

    def get_all(self):

        return self.nodes
