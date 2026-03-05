from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .volume import Volume


class DiskGroupState(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


@dataclass
class DiskGroup:

    name: str
    state: DiskGroupState

    volumes: List[Volume] = field(default_factory=list)
    node: Optional[str] = None

    @property
    def total_size_gb(self) -> int:
        return sum(v.size_gb for v in self.volumes)

    @property
    def volume_count(self) -> int:
        return len(self.volumes)