from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Issue:

    message: str
    severity: str = "WARNING"
    source: str = "SYSTEM"
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self):

        return {
            "message": self.message,
            "severity": self.severity,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }
