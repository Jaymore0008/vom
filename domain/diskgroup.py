# vom/domain/diskgroup.py

from dataclasses import dataclass, field
from typing import List
from .volume import Volume


@dataclass
class DiskGroup:

    name: str
    state: str
    volumes: List[Volume] = field(default_factory=list)
    node: str = None

    def total_size_gb(self):

        return sum(v.size_gb for v in self.volumes)

    def volume_count(self):

        return len(self.volumes)

    def to_dict(self):

        return {
            "name": self.name,
            "state": self.state,
            "total_size_gb": self.total_size_gb(),
            "volume_count": self.volume_count(),
            "node": self.node
        }
