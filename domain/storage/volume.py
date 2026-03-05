from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VolumeLayout(Enum):
    STRIPE = "STRIPE"
    CONCAT = "CONCAT"


@dataclass
class Volume:

    name: str
    diskgroup: str
    size_gb: int
    layout: VolumeLayout

    mount_point: Optional[str] = None
    mounted: bool = False
    node: Optional[str] = None

    def is_striped(self) -> bool:
        return self.layout == VolumeLayout.STRIPE

    def is_concat(self) -> bool:
        return self.layout == VolumeLayout.CONCAT
