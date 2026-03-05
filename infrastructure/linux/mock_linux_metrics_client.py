# vom/infrastructure/mock_linux_metrics_client.py

import random
from datetime import datetime

from domain.monitoring.metric_snapshot import MetricSnapshot
from .linux_metrics_base import BaseLinuxMetricsClient


class MockLinuxMetricsClient(BaseLinuxMetricsClient):

    def __init__(self, host: str):
        self.host = host

    def collect(self) -> MetricSnapshot:

        return MetricSnapshot(
            host=self.host,
            cpu_usage=round(random.uniform(10, 85), 2),
            memory_usage=round(random.uniform(20, 90), 2),
            timestamp=datetime.now()
        )