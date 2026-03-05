# vom/domain/alert.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertMetric(Enum):
    CPU = "CPU"
    MEMORY = "MEMORY"
    STATUS = "STATUS"


@dataclass
class Alert:
    host: str
    message: str
    severity: AlertSeverity
    metric: AlertMetric
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "message": self.message,
            "severity": self.severity.value,
            "metric": self.metric.value,
            "timestamp": self.timestamp.isoformat()
        }