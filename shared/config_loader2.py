# vom/shared/config_loader.py

import yaml
from pathlib import Path
from typing import Dict

from shared.config import AppConfig


class ConfigLoader:

    def __init__(self, config_path: str = "config/hosts.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load()

    def _load(self) -> AppConfig:

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r") as f:
            raw = yaml.safe_load(f)

        linux_hosts: Dict[str, str] = raw.get("linux_hosts", {})

        settings = raw.get("settings", {})

        return AppConfig(
            linux_hosts=linux_hosts,
            max_workers=settings.get("max_workers", 20),
            ssh_user=settings.get("ssh_user", "root")
        )

    def get_linux_hosts(self) -> Dict[str, str]:
        return self._config.linux_hosts

    def get_max_workers(self) -> int:
        return self._config.max_workers

    def get_ssh_user(self) -> str:
        return self._config.ssh_user