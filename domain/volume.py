# vom/domain/volume.py

from dataclasses import dataclass


@dataclass
class Volume:

    name: str
    diskgroup: str
    size_gb: int
    layout: str
    mount_point: str = None
    mounted: bool = False
    node: str = None

    def is_striped(self):
        return self.layout.lower() == "stripe"

    def is_concat(self):
        return self.layout.lower() == "concat"

    def to_dict(self):
        return {
            "name": self.name,
            "diskgroup": self.diskgroup,
            "size_gb": self.size_gb,
            "layout": self.layout,
            "mount_point": self.mount_point,
            "mounted": self.mounted,
            "node": self.node
        }
