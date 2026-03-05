from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IssueSeverity(Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class IssueSource(Enum):
    SYSTEM = "SYSTEM"
    SERVICE_GROUP = "SERVICE_GROUP"
    FILESYSTEM = "FILESYSTEM"
    NODE = "NODE"
    HOST = "HOST"


@dataclass
class Issue:

    message: str
    severity: IssueSeverity = IssueSeverity.WARNING
    source: IssueSource = IssueSource.SYSTEM
    timestamp: datetime = field(default_factory=datetime.now)