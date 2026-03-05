from dataclasses import dataclass
from typing import Optional

from ..monitoring.health import HealthStatus


CRITICAL_THRESHOLD = 90
WARNING_THRESHOLD = 75


@dataclass
class Filesystem:

    device: str
    mount_point: str
    size_gb: int
    used_gb: int
    available_gb: int
    percent_used: int
    node: Optional[str] = None

    def is_critical(self) -> bool:
        return self.percent_used >= CRITICAL_THRESHOLD

    def is_warning(self) -> bool:
        return WARNING_THRESHOLD <= self.percent_used < CRITICAL_THRESHOLD

    @property
    def health(self) -> HealthStatus:

        if self.is_critical():
            return HealthStatus.CRITICAL

        if self.is_warning():
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY