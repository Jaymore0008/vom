from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ServiceGroup:
    name: str
    node_states: Dict[str, str] = field(default_factory=dict)

    def set_state(self, node: str, state: str):
        self.node_states[node] = state

    def is_offline_everywhere(self) -> bool:
        if not self.node_states:
            return False
        return all(state.upper() != "ONLINE" for state in self.node_states.values())

    def health(self) -> str:
        if not self.node_states:
            return "UNKNOWN"

        if self.is_offline_everywhere():
            return "CRITICAL"

        if any(state.upper() != "ONLINE" for state in self.node_states.values()):
            return "WARNING"

        return "HEALTHY"
