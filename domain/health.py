# vom/domain/health.py

from enum import Enum


class HealthStatus(Enum):

    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
