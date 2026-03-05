# vom/domain/metric_snapshot.py

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricSnapshot:
    host: str
    cpu_usage: float
    memory_usage: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "timestamp": self.timestamp.isoformat()
        }