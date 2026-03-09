# vom/application/collectors/linux_collector.py

"""
LinuxCollector

Responsible for collecting Linux host metrics and constructing
Host domain objects.

Responsibilities:
- use LinuxMetricsClient to collect metrics
- build Host domain objects
- return Host instance
"""

import logging
from datetime import datetime

from domain.infrastructure.host import Host, HostStatus
from infrastructure.linux.linux_metrics_factory import create_linux_metrics_client


class LinuxCollector:

    def __init__(self, host_name: str, host_ip: str, username: str = "root"):

        self.host_name = host_name
        self.host_ip = host_ip
        self.username = username

    # --------------------------------------------------
    # Collect metrics for a single host
    # --------------------------------------------------

    def collect(self) -> Host:

        client = create_linux_metrics_client(
            host=self.host_ip,
            username=self.username
        )

        try:

            data = client.collect()

            status = HostStatus.UP if data["status"] == "UP" else HostStatus.DOWN

            host = Host(
                name=self.host_name,
                ip=self.host_ip,
                status=status,
                cpu_usage=data["cpu"],
                memory_usage=data["memory"],
                last_updated=datetime.now()
            )

            logging.info(
                f"[LinuxCollector] {self.host_name} CPU={host.cpu_usage}% MEM={host.memory_usage}%"
            )

            return host

        except Exception as e:

            logging.error(
                f"[LinuxCollector] Failed to collect metrics for {self.host_name}: {e}"
            )

            return Host(
                name=self.host_name,
                ip=self.host_ip,
                status=HostStatus.DOWN,
                cpu_usage=0.0,
                memory_usage=0.0,
                last_updated=datetime.now()
            )

        finally:

            try:
                client.close()
            except Exception:
                pass