from dataclasses import dataclass, field
from enum import Enum
from typing import Dict

from ..monitoring.health import HealthStatus


class ServiceGroupState(Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    FAULTED = "FAULTED"
    UNKNOWN = "UNKNOWN"


@dataclass
class ServiceGroup:

    name: str
    node_states: Dict[str, ServiceGroupState] = field(default_factory=dict)

    def set_state(self, node: str, state: ServiceGroupState):
        self.node_states[node] = state

    def is_offline_everywhere(self) -> bool:

        if not self.node_states:
            return False

        return all(state != ServiceGroupState.ONLINE for state in self.node_states.values())

    @property
    def health(self) -> HealthStatus:

        if not self.node_states:
            return HealthStatus.UNKNOWN

        if self.is_offline_everywhere():
            return HealthStatus.CRITICAL

        if any(state != ServiceGroupState.ONLINE for state in self.node_states.values()):
            return HealthStatus.WARNING

        return HealthStatus.HEALTHY
