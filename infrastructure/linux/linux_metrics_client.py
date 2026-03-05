# vom/infrastructure/linux_metrics_client.py

import logging
from datetime import datetime

from domain.monitoring.metric_snapshot import MetricSnapshot
from .linux_metrics_base import BaseLinuxMetricsClient
from ..exceptions.metrics_exceptions import MetricsCollectionError


class LinuxMetricsClient(BaseLinuxMetricsClient):

    def __init__(self, ssh_client, host: str):
        self.host = host
        self.ssh = ssh_client

    # ----------------------------------
    # CPU via mpstat
    # ----------------------------------

    def _get_cpu_usage(self) -> float:

        cmd = "mpstat 1 1"
        exit_code, output, error = self.ssh.execute(cmd)

        if exit_code != 0:
            raise MetricsCollectionError(f"mpstat failed: {error}")

        for line in output.splitlines():
            if "Average:" in line and "all" in line:
                parts = line.split()
                idle = float(parts[-1])
                return round(100 - idle, 2)

        raise MetricsCollectionError("Unable to parse mpstat output")

    # ----------------------------------
    # Memory via free -m
    # ----------------------------------

    def _get_memory_usage(self) -> float:

        cmd = "free -m"
        exit_code, output, error = self.ssh.execute(cmd)

        if exit_code != 0:
            raise MetricsCollectionError(f"free failed: {error}")

        for line in output.splitlines():
            if line.startswith("Mem:"):
                parts = line.split()
                total = float(parts[1])
                used = float(parts[2])
                return round((used / total) * 100, 2)

        raise MetricsCollectionError("Unable to parse free output")

    # ----------------------------------
    # Public Collect
    # ----------------------------------

    def collect(self) -> MetricSnapshot:

        try:
            cpu = self._get_cpu_usage()
            memory = self._get_memory_usage()

            return MetricSnapshot(
                host=self.host,
                cpu_usage=cpu,
                memory_usage=memory,
                timestamp=datetime.now()
            )

        except Exception as e:
            logging.error(f"[LinuxMetrics] {self.host} failed: {e}")
            raise MetricsCollectionError(str(e))

    def close(self):
        self.ssh.close()