# vom/domain/filesystem.py

from dataclasses import dataclass


@dataclass
class Filesystem:

    device: str
    mount_point: str
    size_gb: int
    used_gb: int
    available_gb: int
    percent_used: int
    node: str = None

    def is_critical(self):
        return self.percent_used >= 90

    def is_warning(self):
        return self.percent_used >= 75

    def to_dict(self):
        return {
            "device": self.device,
            "mount_point": self.mount_point,
            "size_gb": self.size_gb,
            "used_gb": self.used_gb,
            "available_gb": self.available_gb,
            "percent_used": self.percent_used,
            "node": self.node
        }
