# vom/application/services/host_service.py

"""
HostService

Application service responsible for Linux host monitoring.

Responsibilities:
- load hosts from config
- collect host metrics in parallel
- return Host domain objects
"""

import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from domain.host import Host, HostStatus
from application.collectors.linux_collector import LinuxCollector
from shared.config_loader import ConfigLoader


class HostService:

    def __init__(self, max_workers: int = 20):

        self.max_workers = max_workers
        self.config = ConfigLoader()

    # --------------------------------------------------
    # Collect metrics for a single host
    # --------------------------------------------------

    def _collect_single(self, host_name: str, host_ip: str) -> Host:

        collector = LinuxCollector(
            host_name=host_name,
            host_ip=host_ip
        )

        return collector.collect()

    # --------------------------------------------------
    # Collect metrics for all hosts
    # --------------------------------------------------

    def collect_all(self) -> List[Host]:

        hosts_config = self.config.get_linux_hosts()

        results: List[Host] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            future_map = {
                executor.submit(self._collect_single, name, ip): (name, ip)
                for name, ip in hosts_config.items()
            }

            for future in as_completed(future_map):

                name, ip = future_map[future]

                try:

                    host = future.result(timeout=10)

                    results.append(host)

                except Exception as e:

                    logging.error(
                        f"[HostService] Failed collecting host {name}: {e}"
                    )

                    results.append(
                        Host(
                            name=name,
                            ip=ip,
                            status=HostStatus.DOWN,
                            cpu_usage=0.0,
                            memory_usage=0.0
                        )
                    )

        return results

    # --------------------------------------------------
    # Utility helpers
    # --------------------------------------------------

    @staticmethod
    def top_cpu(hosts: List[Host], n: int = 5) -> List[Host]:

        return sorted(
            hosts,
            key=lambda h: h.cpu_usage,
            reverse=True
        )[:n]

    @staticmethod
    def top_memory(hosts: List[Host], n: int = 5) -> List[Host]:

        return sorted(
            hosts,
            key=lambda h: h.memory_usage,
            reverse=True
        )[:n]

    @staticmethod
    def down_hosts(hosts: List[Host]) -> List[Host]:

        return [
            h for h in hosts
            if h.status == HostStatus.DOWN
        ]