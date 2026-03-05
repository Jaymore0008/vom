# vom/domain/host.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class HostStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    MAINTENANCE = "MAINTENANCE"   # Future-ready
    UNKNOWN = "UNKNOWN"           # Future-ready


class HostHealth(Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Host:
    name: str
    ip: str
    status: HostStatus

    cpu_usage: float = 0.0
    memory_usage: float = 0.0

    last_updated: datetime = field(default_factory=datetime.now)

    # -----------------------------
    # Health Logic
    # -----------------------------

    def cpu_health(self) -> HostHealth:
        if self.cpu_usage >= 90:
            return HostHealth.CRITICAL
        if self.cpu_usage >= 75:
            return HostHealth.WARNING
        return HostHealth.HEALTHY

    def memory_health(self) -> HostHealth:
        if self.memory_usage >= 90:
            return HostHealth.CRITICAL
        if self.memory_usage >= 75:
            return HostHealth.WARNING
        return HostHealth.HEALTHY

    def overall_health(self) -> HostHealth:

        # Maintenance logic example
        if self.status == HostStatus.MAINTENANCE:
            return HostHealth.HEALTHY

        if self.status == HostStatus.DOWN:
            return HostHealth.CRITICAL

        cpu = self.cpu_health()
        memory = self.memory_health()

        healths = [cpu, memory]

        if HostHealth.CRITICAL in healths:
            return HostHealth.CRITICAL

        if HostHealth.WARNING in healths:
            return HostHealth.WARNING

        return HostHealth.HEALTHY

    # -----------------------------
    # Serialization (optional)
    # -----------------------------

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ip": self.ip,
            "status": self.status.value,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "overall_health": self.overall_health().value,
            "last_updated": self.last_updated.isoformat()
        }