# vom/application/host_service.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Callable
import logging

from domain.infrastructure.host import Host, HostStatus
from domain.monitoring.metric_snapshot import MetricSnapshot
from infrastructure.exceptions.metrics_exceptions import MetricsCollectionError


class HostService:

    def __init__(
        self,
        config_loader,
        metrics_client_factory: Callable[[str], object],
        max_workers: int = 20
    ):
        self.max_workers = max_workers
        self.config = config_loader
        self.metrics_client_factory = metrics_client_factory

    # ---------------------------------------
    # Collect metrics for one host
    # ---------------------------------------

    def _collect_single(self, host_name: str, host_ip: str) -> Host:

        client = self.metrics_client_factory(host_ip)

        try:
            snapshot: MetricSnapshot = client.collect()

            return Host(
                name=host_name,
                ip=host_ip,
                status=HostStatus.UP,
                cpu_usage=snapshot.cpu_usage,
                memory_usage=snapshot.memory_usage,
                last_updated=snapshot.timestamp
            )

        except MetricsCollectionError as e:

            logging.error(f"[HostService] {host_name} failed: {e}")

            return Host(
                name=host_name,
                ip=host_ip,
                status=HostStatus.DOWN,
                cpu_usage=0.0,
                memory_usage=0.0,
                last_updated=datetime.now()
            )

    # ---------------------------------------
    # Collect all hosts in parallel
    # ---------------------------------------

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
                    host = future.result(timeout=5)
                    results.append(host)

                except Exception as e:
                    logging.error(f"[HostService] {name} execution failed: {e}")

                    results.append(
                        Host(
                            name=name,
                            ip=ip,
                            status=HostStatus.DOWN,
                            cpu_usage=0.0,
                            memory_usage=0.0,
                            last_updated=datetime.now()
                        )
                    )

        return results

    # ---------------------------------------
    # Top N utilities
    # ---------------------------------------

    @staticmethod
    def top_cpu(hosts: List[Host], n: int = 5) -> List[Host]:
        return sorted(hosts, key=lambda h: h.cpu_usage, reverse=True)[:n]

    @staticmethod
    def top_memory(hosts: List[Host], n: int = 5) -> List[Host]:
        return sorted(hosts, key=lambda h: h.memory_usage, reverse=True)[:n]

    @staticmethod
    def down_hosts(hosts: List[Host]) -> List[Host]:
        return [h for h in hosts if h.status == HostStatus.DOWN] 