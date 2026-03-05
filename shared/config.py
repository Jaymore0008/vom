from dataclasses import dataclass
from typing import Dict


@dataclass
class AppConfig:
    linux_hosts: Dict[str, str]
    max_workers: int
    ssh_user: str