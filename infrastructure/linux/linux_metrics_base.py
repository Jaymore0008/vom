# vom/infrastructure/linux_metrics_base.py

from abc import ABC, abstractmethod
from domain.monitoring.metric_snapshot import MetricSnapshot


class BaseLinuxMetricsClient(ABC):

    @abstractmethod
    def collect(self) -> MetricSnapshot:
        """
        Collects metrics from a host and returns a MetricSnapshot.
        Raises MetricsCollectionError if collection fails.
        """
        pass